# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0cpubsub.proto\x12\x1d\x61\x65\x61.eightballer.pubsub.v0_1_0"\xc2\x08\n\rPubsubMessage\x12P\n\x05\x65rror\x18\x05 \x01(\x0b\x32?.aea.eightballer.pubsub.v0_1_0.PubsubMessage.Error_PerformativeH\x00\x12T\n\x07message\x18\x06 \x01(\x0b\x32\x41.aea.eightballer.pubsub.v0_1_0.PubsubMessage.Message_PerformativeH\x00\x12T\n\x07publish\x18\x07 \x01(\x0b\x32\x41.aea.eightballer.pubsub.v0_1_0.PubsubMessage.Publish_PerformativeH\x00\x12X\n\tsubscribe\x18\x08 \x01(\x0b\x32\x43.aea.eightballer.pubsub.v0_1_0.PubsubMessage.Subscribe_PerformativeH\x00\x12Z\n\nsubscribed\x18\t \x01(\x0b\x32\x44.aea.eightballer.pubsub.v0_1_0.PubsubMessage.Subscribed_PerformativeH\x00\x12\\\n\x0bunsubscribe\x18\n \x01(\x0b\x32\x45.aea.eightballer.pubsub.v0_1_0.PubsubMessage.Unsubscribe_PerformativeH\x00\x12^\n\x0cunsubscribed\x18\x0b \x01(\x0b\x32\x46.aea.eightballer.pubsub.v0_1_0.PubsubMessage.Unsubscribed_PerformativeH\x00\x1a*\n\x16Subscribe_Performative\x12\x10\n\x08\x63hannels\x18\x01 \x03(\t\x1a,\n\x18Unsubscribe_Performative\x12\x10\n\x08\x63hannels\x18\x01 \x03(\t\x1a\x38\n\x14Publish_Performative\x12\x0f\n\x07\x63hannel\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\x0c\x1a^\n\x17Subscribed_Performative\x12\x0f\n\x07\x63hannel\x18\x01 \x01(\t\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x0c\n\x04info\x18\x03 \x01(\t\x12\x13\n\x0binfo_is_set\x18\x04 \x01(\x08\x1a`\n\x19Unsubscribed_Performative\x12\x0f\n\x07\x63hannel\x18\x01 \x01(\t\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x0c\n\x04info\x18\x03 \x01(\t\x12\x13\n\x0binfo_is_set\x18\x04 \x01(\x08\x1a\x35\n\x14Message_Performative\x12\x0f\n\x07\x63hannel\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x1a"\n\x12\x45rror_Performative\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x42\x0e\n\x0cperformativeb\x06proto3'
)


_PUBSUBMESSAGE = DESCRIPTOR.message_types_by_name["PubsubMessage"]
_PUBSUBMESSAGE_SUBSCRIBE_PERFORMATIVE = _PUBSUBMESSAGE.nested_types_by_name[
    "Subscribe_Performative"
]
_PUBSUBMESSAGE_UNSUBSCRIBE_PERFORMATIVE = _PUBSUBMESSAGE.nested_types_by_name[
    "Unsubscribe_Performative"
]
_PUBSUBMESSAGE_PUBLISH_PERFORMATIVE = _PUBSUBMESSAGE.nested_types_by_name[
    "Publish_Performative"
]
_PUBSUBMESSAGE_SUBSCRIBED_PERFORMATIVE = _PUBSUBMESSAGE.nested_types_by_name[
    "Subscribed_Performative"
]
_PUBSUBMESSAGE_UNSUBSCRIBED_PERFORMATIVE = _PUBSUBMESSAGE.nested_types_by_name[
    "Unsubscribed_Performative"
]
_PUBSUBMESSAGE_MESSAGE_PERFORMATIVE = _PUBSUBMESSAGE.nested_types_by_name[
    "Message_Performative"
]
_PUBSUBMESSAGE_ERROR_PERFORMATIVE = _PUBSUBMESSAGE.nested_types_by_name[
    "Error_Performative"
]
PubsubMessage = _reflection.GeneratedProtocolMessageType(
    "PubsubMessage",
    (_message.Message,),
    {
        "Subscribe_Performative": _reflection.GeneratedProtocolMessageType(
            "Subscribe_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PUBSUBMESSAGE_SUBSCRIBE_PERFORMATIVE,
                "__module__": "pubsub_pb2"
                # @@protoc_insertion_point(class_scope:aea.eightballer.pubsub.v0_1_0.PubsubMessage.Subscribe_Performative)
            },
        ),
        "Unsubscribe_Performative": _reflection.GeneratedProtocolMessageType(
            "Unsubscribe_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PUBSUBMESSAGE_UNSUBSCRIBE_PERFORMATIVE,
                "__module__": "pubsub_pb2"
                # @@protoc_insertion_point(class_scope:aea.eightballer.pubsub.v0_1_0.PubsubMessage.Unsubscribe_Performative)
            },
        ),
        "Publish_Performative": _reflection.GeneratedProtocolMessageType(
            "Publish_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PUBSUBMESSAGE_PUBLISH_PERFORMATIVE,
                "__module__": "pubsub_pb2"
                # @@protoc_insertion_point(class_scope:aea.eightballer.pubsub.v0_1_0.PubsubMessage.Publish_Performative)
            },
        ),
        "Subscribed_Performative": _reflection.GeneratedProtocolMessageType(
            "Subscribed_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PUBSUBMESSAGE_SUBSCRIBED_PERFORMATIVE,
                "__module__": "pubsub_pb2"
                # @@protoc_insertion_point(class_scope:aea.eightballer.pubsub.v0_1_0.PubsubMessage.Subscribed_Performative)
            },
        ),
        "Unsubscribed_Performative": _reflection.GeneratedProtocolMessageType(
            "Unsubscribed_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PUBSUBMESSAGE_UNSUBSCRIBED_PERFORMATIVE,
                "__module__": "pubsub_pb2"
                # @@protoc_insertion_point(class_scope:aea.eightballer.pubsub.v0_1_0.PubsubMessage.Unsubscribed_Performative)
            },
        ),
        "Message_Performative": _reflection.GeneratedProtocolMessageType(
            "Message_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PUBSUBMESSAGE_MESSAGE_PERFORMATIVE,
                "__module__": "pubsub_pb2"
                # @@protoc_insertion_point(class_scope:aea.eightballer.pubsub.v0_1_0.PubsubMessage.Message_Performative)
            },
        ),
        "Error_Performative": _reflection.GeneratedProtocolMessageType(
            "Error_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _PUBSUBMESSAGE_ERROR_PERFORMATIVE,
                "__module__": "pubsub_pb2"
                # @@protoc_insertion_point(class_scope:aea.eightballer.pubsub.v0_1_0.PubsubMessage.Error_Performative)
            },
        ),
        "DESCRIPTOR": _PUBSUBMESSAGE,
        "__module__": "pubsub_pb2"
        # @@protoc_insertion_point(class_scope:aea.eightballer.pubsub.v0_1_0.PubsubMessage)
    },
)
_sym_db.RegisterMessage(PubsubMessage)
_sym_db.RegisterMessage(PubsubMessage.Subscribe_Performative)
_sym_db.RegisterMessage(PubsubMessage.Unsubscribe_Performative)
_sym_db.RegisterMessage(PubsubMessage.Publish_Performative)
_sym_db.RegisterMessage(PubsubMessage.Subscribed_Performative)
_sym_db.RegisterMessage(PubsubMessage.Unsubscribed_Performative)
_sym_db.RegisterMessage(PubsubMessage.Message_Performative)
_sym_db.RegisterMessage(PubsubMessage.Error_Performative)

if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _PUBSUBMESSAGE._serialized_start = 48
    _PUBSUBMESSAGE._serialized_end = 1138
    _PUBSUBMESSAGE_SUBSCRIBE_PERFORMATIVE._serialized_start = 691
    _PUBSUBMESSAGE_SUBSCRIBE_PERFORMATIVE._serialized_end = 733
    _PUBSUBMESSAGE_UNSUBSCRIBE_PERFORMATIVE._serialized_start = 735
    _PUBSUBMESSAGE_UNSUBSCRIBE_PERFORMATIVE._serialized_end = 779
    _PUBSUBMESSAGE_PUBLISH_PERFORMATIVE._serialized_start = 781
    _PUBSUBMESSAGE_PUBLISH_PERFORMATIVE._serialized_end = 837
    _PUBSUBMESSAGE_SUBSCRIBED_PERFORMATIVE._serialized_start = 839
    _PUBSUBMESSAGE_SUBSCRIBED_PERFORMATIVE._serialized_end = 933
    _PUBSUBMESSAGE_UNSUBSCRIBED_PERFORMATIVE._serialized_start = 935
    _PUBSUBMESSAGE_UNSUBSCRIBED_PERFORMATIVE._serialized_end = 1031
    _PUBSUBMESSAGE_MESSAGE_PERFORMATIVE._serialized_start = 1033
    _PUBSUBMESSAGE_MESSAGE_PERFORMATIVE._serialized_end = 1086
    _PUBSUBMESSAGE_ERROR_PERFORMATIVE._serialized_start = 1088
    _PUBSUBMESSAGE_ERROR_PERFORMATIVE._serialized_end = 1122
# @@protoc_insertion_point(module_scope)
