# ------------------------------------------------------------------------------
#
#   Copyright 2023 eightballer
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""Scaffold connection and channel."""

import ssl
import asyncio
import contextlib
from typing import Any, cast
from asyncio import CancelledError
from textwrap import dedent
from asyncio.events import AbstractEventLoop
from asyncio.futures import Future
from concurrent.futures._base import CancelledError as FuturesCancelledError  # noqa

import socketio
from aiohttp import WSMessage, web
from aea.common import Address
from aea.mail.base import Message, Envelope
from aiohttp.web_request import BaseRequest
from aea.configurations.base import PublicId
from aea.protocols.dialogue.base import Dialogue as BaseDialogue, DialogueLabel

from packages.eightballer.protocols.http.message import HttpMessage
from packages.eightballer.protocols.http.dialogues import (
    HttpDialogues as BaseHttpDialogues,
)
from packages.eightballer.protocols.websockets.message import WebsocketsMessage
from packages.eightballer.protocols.websockets.dialogues import (
    WebsocketsDialogue,
    WebsocketsDialogues as BaseWebsocketsDialogues,
)
from packages.eightballer.connections.http_server.connection import (
    NOT_FOUND,
    Request as HttpRequest,
    HTTPChannel,
    HTTPServerConnection,
)


CONNECTION_ID = PublicId.from_str("eightballer/websocket_server:0.1.0")


class WebSocketDialogue(BaseWebsocketsDialogues):
    """The dialogues class keeps track of all http dialogues."""

    def __init__(self, self_address: Address = None, **kwargs: Any) -> None:
        """Initialize dialogues."""
        del self_address

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message, receiver_address: Address
        ) -> BaseDialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message."""
            del receiver_address, message
            return WebsocketsDialogue.Role.SERVER

        BaseWebsocketsDialogues.__init__(
            self,
            self_address=str(CONNECTION_ID),
            role_from_first_message=role_from_first_message,
            **kwargs,
        )


RequestId = DialogueLabel


class WebSocketChannel(HTTPChannel):
    """A wrapper for an RESTful API with an internal HTTPServer."""

    RESPONSE_TIMEOUT = 6

    def __init__(self, **kwarg):
        super().__init__(**kwarg)
        self.open_connections: dict[RequestId, Future] = {}
        self._websocket_dialogues = WebSocketDialogue(self.address)
        self.wss_server = None

    async def _base_connect(self, loop: AbstractEventLoop) -> None:
        """Connect.

        Upon HTTP Channel connection, start the HTTP Server in its own thread.

        """
        self._loop = loop
        self._in_queue = asyncio.Queue()
        self.is_stopped = False
        self.pending_requests: dict[dict[str]] = {}

    async def connect(self, loop: AbstractEventLoop) -> None:
        """Connect.

        Upon HTTP Channel connection, start the HTTP Server in its own thread.

        """
        if self.is_stopped:
            await self._base_connect(loop)

            try:
                await self._start_ws_server()
                self.logger.info(f"WebSocket Server has connected to port: {self.port}.")
            except Exception:  # pragma: nocover # pylint: disable=broad-except
                self.is_stopped = True
                self._in_queue = None
                self.logger.exception(f"Failed to start server on {self.host}:{self.port}.")

    async def _http_handler(self, http_request: BaseRequest):
        """Verify the request then send the request to Agent as an envelope.

        Note, this message handles the initiall http connection for the websocket.

        We use that to create a mapping of the request id to the future object.

        """
        self.logger.info(f"Handling initial http request for websocket connection from {http_request.remote}")
        connection_time = self._loop.time()
        request = await HttpRequest.create(http_request)
        ws = web.WebSocketResponse()
        await ws.prepare(http_request)

        if self._in_queue is None:  # pragma: nocover
            msg = "Channel not connected!"
            raise ValueError(msg)

        is_valid_request = self.api_spec.verify(request)

        if not is_valid_request:
            self.logger.warning(f"request is not valid: {request}")
            return BaseHttpDialogues(  # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
                status=NOT_FOUND, reason="Request Not Found"
            )

        try:
            # turn request into envelope
            http_envelope = request.to_envelope_and_set_id(self._dialogues, self.target_skill_id)

            self.open_connections[request.id] = Future()
            self.open_connections[request.id].ws = ws
            # send the envelope to the agent's inbox (via self.in_queue)
            await self._in_queue.put(http_envelope)
            await self._handle_new_client(request, ws=ws)

            # we now wait for ws messages to come in.
            while self._loop.time() - connection_time < self.RESPONSE_TIMEOUT:
                if self.open_connections[request.id].done():
                    break
                async for msg in ws:
                    websocket_envelope = await self._inbound_wss_handler(request, msg)
                    await self._in_queue.put(websocket_envelope)
                    break
                await asyncio.sleep(0.0000001)

            # this is the closure http response.
            self.logger.info(f"Closing initial connection from {request.id}")
            await self.close_session(request.id, ws)

        except TimeoutError as err:
            self.logger.warning(
                dedent(f"""
                Request timed out! Request={request} not handled as a result.
                Ensure requests (protocol_id={HttpMessage.protocol_id}) are handled by a skill!"
                """)
            )
            raise NotImplementedError from err
        except FuturesCancelledError as err:
            raise NotImplementedError from err
        except BaseException as err:
            self.logger.exception("Error during handling incoming request")
            raise NotImplementedError from err
        finally:
            self.logger.info("About to finish handling inital http response!")
            if request.is_id_set:
                self.open_connections.pop(request.id, None)

    async def close_session(self, request_id: RequestId, ws) -> None:
        """Close the connection."""
        with contextlib.suppress(AttributeError):
            await ws.close()
        dialogue = self.pending_requests.pop(request_id, None)
        if dialogue is not None:
            msg = dialogue.reply(
                performative=WebsocketsMessage.Performative.DISCONNECT,
            )
            self.logger.info(f"Closed websocket dialogue for request id: {request_id}")
            self.open_connections.pop(request_id, None)
            await self.send_msg_to_agent(msg)

    async def send_msg_to_agent(self, msg):
        """Send a message to the agent."""
        envelope = Envelope(
            to=str(self.target_skill_id),
            sender=str(self.connection_id),
            message=msg,
        )
        await self._in_queue.put(envelope)

    async def _inbound_wss_handler(self, http_request: BaseRequest, websocket_message: WSMessage):
        """Verify the request then send the request to Agent as an envelope.

        Note, this message handles the initiall http connection for the websocket.

        We use that to create a mapping of the request id to the future object.
        """
        if self._in_queue is None:  # pragma: nocover
            msg = "Channel not connected!"
            raise ValueError(msg)

        self.logger.debug(f"Received inbound message from websocket client: {websocket_message}")

        msg, _ = await self._handle_existing_client(http_request, websocket_message)
        # we need to get the existing request.
        await self.send_msg_to_agent(msg)

    async def _handle_new_client(self, http_request: BaseRequest = None, url=None, sid=None, sio=None, ws=None) -> None:
        """We want to create our reponse which will basically be the websocket connection."""
        if url is None and http_request is not None:
            url = http_request.id.get_incomplete_version().dialogue_reference[0]

        session_id = http_request.id if http_request is not None else sid

        request, dialogue = self._websocket_dialogues.create(
            counterparty=str(self.target_skill_id),
            performative=WebsocketsMessage.Performative.CONNECT,
            url=url,
        )
        # we should really handle this later.
        dialogue.reply(
            performative=WebsocketsMessage.Performative.CONNECTION_ACK,
            success=True,
        )
        if sio is not None:
            dialogue.ws = sio

            async def send_str(data):
                self.logger.debug(f"Sending data to client: {data}")
                await sio.emit("data", data)

            dialogue.ws.send_str = send_str
        if ws is not None:
            dialogue.ws = ws

        self.open_connections[sid] = dialogue
        self.pending_requests[session_id] = dialogue
        await self.send_msg_to_agent(request)
        return request, dialogue

    async def _handle_existing_client(self, http_request: BaseRequest, websocket_message: WSMessage) -> None:
        """Retrieve the existing request and add the message to the queue."""
        websocket_dialogue = self.pending_requests[http_request.id]
        # we need to get the existing request.
        request = websocket_dialogue.reply(
            performative=WebsocketsMessage.Performative.SEND,
            data=websocket_message.data,
        )
        return request, websocket_dialogue

    async def _start_ws_server(self) -> None:
        """Start websocket server."""
        loop = asyncio.get_event_loop()
        app = web.Application(loop=loop)
        sio = socketio.AsyncServer(cors_allowed_origins="*")
        sio.attach(app)

        @sio.on("*")
        async def catch_all(event, sid, data):
            if event in {"connect", "disconnect", "agent"}:
                return
            self.logger.debug(f"Received message from client: {event}")

            dialogue = self.open_connections.get(sid, None)
            if dialogue is None:
                msg, dialogue = await self._handle_new_client(sid=sid, url=event)
                await self.send_msg_to_agent(msg)

            msg = dialogue.reply(
                performative=WebsocketsMessage.Performative.SEND,
                data=data,
            )
            await self.send_msg_to_agent(msg)

        @sio.on("connect")
        async def connect(sid, environ):
            self.logger.info(f"Received connection from client: {sid}")
            msg, _ = await self._handle_new_client(sid=sid, url=environ["PATH_INFO"], sio=sio)
            await self.send_msg_to_agent(msg)

        @sio.on("disconnect")
        async def disconnect(sid):
            with contextlib.suppress(AttributeError):
                await self.close_session(sid, sio)
            self.logger.info(f"Closed websocket dialogue for request id: {sid}")
            dialogues = self.pending_requests.pop(sid, None)
            if dialogues is not None:
                await self.close_session(sid, sio)
                self.logger.info(f"Closed websocket dialogue for request id: {sid}")
            session = self.open_connections.pop(sid, None)
            if session is not None:
                await self.close_session(sid, sio)
                self.logger.info(f"Closed websocket dialogue for request id: {sid}")

        app.router.add_get("/{tail:.*}", self._http_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        ssl_context = None
        if self.ssl_cert_path and self.ssl_key_path:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(self.ssl_cert_path, self.ssl_key_path)
        self.wss_server = web.TCPSite(runner, self.host, self.port, ssl_context=ssl_context)
        await self.wss_server.start()

    async def send(self, envelope: Envelope) -> None:  # pylint: disable=W0236
        """Send the envelope in_queue."""
        if self.wss_server is None:  # pragma: nocover
            msg = "Server not connected, call connect first!"
            raise ValueError(msg)

        message = cast(WebsocketsMessage, envelope.message)
        if envelope.protocol_specification_id == HttpMessage.protocol_id:
            dialogue = self._dialogues.update(message)
            future = self.open_connections.pop(dialogue.incomplete_dialogue_label, None)
        elif envelope.protocol_specification_id == WebsocketsMessage.protocol_id:
            dialogue = self._websocket_dialogues.update(message)
            future = self.pending_requests.pop(dialogue.incomplete_dialogue_label, None)
            await self.send_message_to_client(message, dialogue)
        else:
            msg = f"Unsupported protocol specification id: {envelope.protocol_specification_id}"
            raise ValueError(msg)

        if dialogue is None:
            self.logger.warning(f"Could not create dialogue for message={message}")
            return

        if not future:
            return
        if not future.done():
            future.set_result(message)

    async def send_message_to_client(self, message, dialogue) -> Envelope | None:
        """Send message to a existing client."""
        if message.performative == WebsocketsMessage.Performative.CONNECTION_ACK:
            return None

        ws_dialogues_to_connections = {v.incomplete_dialogue_label: k for k, v in self.pending_requests.items()}
        if message.performative == WebsocketsMessage.Performative.SEND:
            http_dialogue_ref = ws_dialogues_to_connections.get(dialogue.incomplete_dialogue_label, None)
            if http_dialogue_ref is None:
                self.logger.warning(f"Could not locate http dialogue for message={message}")
                msg = dialogue.reply(
                    performative=WebsocketsMessage.Performative.DISCONNECT,
                    reason=f"Could not locate http dialogue for message={message}",
                )
                await self.send_msg_to_agent(msg)
                return None

            try:
                await dialogue.ws.send_str(message.data)
            except ConnectionResetError:
                self.logger.warning(f"Could not locate http dialogue for message={message}")
                msg = dialogue.reply(
                    performative=WebsocketsMessage.Performative.DISCONNECT,
                    reason=f"Could not locate http dialogue for message={message}",
                )
                await self.send_msg_to_agent(msg)
                return None

    async def disconnect(self) -> None:
        """Disconnect.

        Shut-off the HTTP Server.
        """
        if self.wss_server is None:  # pragma: nocover
            msg = "Server not connected, call connect first!"
            raise ValueError(msg)

        if not self.is_stopped:
            await self.wss_server.stop()
            self.logger.info(f"HTTP Server has shutdown on port: {self.port}.")
            self.is_stopped = True
            self._in_queue = None


class WebSocketServerConnection(HTTPServerConnection):
    """Proxy to the functionality of the SDK or API."""

    connection_id = CONNECTION_ID
    max_client_connections = 10
    max_client_age = 1e6
    client_connections = {}

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the connection.

        The configuration must be specified if and only if the following
        parameters are None: connection_id, excluded_protocols or restricted_to_protocols.

        Possible keyword arguments:
        - configuration: the connection configuration.
        - data_dir: directory where to put local files.
        - identity: the identity object held by the agent.
        - crypto_store: the crypto store for encrypted communication.
        - restricted_to_protocols: the set of protocols ids of the only supported protocols for this connection.
        - excluded_protocols: the set of protocols ids that we want to exclude for this connection.

        """

        super().__init__(**kwargs)
        api_spec_path = cast(str | None, self.configuration.config.get("api_spec_path"))
        self.channel = WebSocketChannel(
            address=self.address,
            logger=self.logger,
            connection_id=CONNECTION_ID,
            host=self.channel.host,
            port=self.channel.port,
            target_skill_id=self.channel.target_skill_id,
            api_spec_path=api_spec_path,
        )

    async def connect(self) -> None:
        """Set up the connection.

        In the implementation, remember to update 'connection_status' accordingly.
        """
        await super().connect()

    async def disconnect(self) -> None:
        """Tear down the connection.

        In the implementation, remember to update 'connection_status' accordingly.
        """
        await super().disconnect()

    async def send(self, envelope: Envelope) -> None:
        """Send an envelope back to the client. This is the initial HTTP response."""
        self._ensure_connected()
        # note we dont yet want to send the envelope, we want to wait for the websocket connection
        if envelope.protocol_specification_id == HttpMessage.protocol_id:
            self._dialogues.update(envelope.message)  # pylint: disable=E1101
        elif envelope.protocol_specification_id == WebsocketsMessage.protocol_id:
            await self.channel.send(envelope)

    async def receive(self, *args: Any, **kwargs: Any) -> Envelope | None:
        """Receive an envelope. Blocking."""
        del args, kwargs
        self._ensure_connected()
        # we check if we have enough available connections to handle the new request
        try:
            res = await self.channel.get_message()
            self.logger.debug(f"Received message from agent skill: {res}")
            return res
        except CancelledError:
            return None
