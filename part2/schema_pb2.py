# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: schema.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cschema.proto\x12\x04\x63hat\"\x1d\n\x0b\x43redentials\x12\x0e\n\x06userId\x18\x01 \x01(\t\"-\n\x07\x41\x63\x63ount\x12\x0e\n\x06userId\x18\x01 \x01(\t\x12\x12\n\nisLoggedIn\x18\x02 \x01(\x08\">\n\x07Message\x12\x10\n\x08\x61uthorId\x18\x01 \x01(\t\x12\x13\n\x0brecipientId\x18\x02 \x01(\t\x12\x0c\n\x04text\x18\x03 \x01(\t\"\x0e\n\x0c\x42lankRequest\"\x1f\n\x0bListRequest\x12\x10\n\x08wildcard\x18\x01 \x01(\t\"6\n\rBasicResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x14\n\x0c\x65rrorMessage\x18\x02 \x01(\t\"V\n\x0cListResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x14\n\x0c\x65rrorMessage\x18\x02 \x01(\t\x12\x1f\n\x08\x61\x63\x63ounts\x18\x03 \x03(\x0b\x32\r.chat.Account\"]\n\rFlushResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x14\n\x0c\x65rrorMessage\x18\x02 \x01(\t\x12%\n\x0equeuedMessages\x18\x03 \x03(\x0b\x32\r.chat.Message2\xe0\x02\n\x0b\x43hatHandler\x12\x30\n\x06\x43reate\x12\x11.chat.Credentials\x1a\x13.chat.BasicResponse\x12/\n\x05Login\x12\x11.chat.Credentials\x1a\x13.chat.BasicResponse\x12\x30\n\x06\x44\x65lete\x12\x11.chat.Credentials\x1a\x13.chat.BasicResponse\x12/\n\tSubscribe\x12\x11.chat.Credentials\x1a\r.chat.Message0\x01\x12*\n\x04Send\x12\r.chat.Message\x1a\x13.chat.BasicResponse\x12\x30\n\x05\x46lush\x12\x12.chat.BlankRequest\x1a\x13.chat.FlushResponse\x12-\n\x04List\x12\x11.chat.ListRequest\x1a\x12.chat.ListResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'schema_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CREDENTIALS._serialized_start=22
  _CREDENTIALS._serialized_end=51
  _ACCOUNT._serialized_start=53
  _ACCOUNT._serialized_end=98
  _MESSAGE._serialized_start=100
  _MESSAGE._serialized_end=162
  _BLANKREQUEST._serialized_start=164
  _BLANKREQUEST._serialized_end=178
  _LISTREQUEST._serialized_start=180
  _LISTREQUEST._serialized_end=211
  _BASICRESPONSE._serialized_start=213
  _BASICRESPONSE._serialized_end=267
  _LISTRESPONSE._serialized_start=269
  _LISTRESPONSE._serialized_end=355
  _FLUSHRESPONSE._serialized_start=357
  _FLUSHRESPONSE._serialized_end=450
  _CHATHANDLER._serialized_start=453
  _CHATHANDLER._serialized_end=805
# @@protoc_insertion_point(module_scope)
