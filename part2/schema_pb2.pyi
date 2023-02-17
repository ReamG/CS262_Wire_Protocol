from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Account(_message.Message):
    __slots__ = ["is_logged_in", "user_id"]
    IS_LOGGED_IN_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_logged_in: bool
    user_id: str
    def __init__(self, user_id: _Optional[str] = ..., is_logged_in: bool = ...) -> None: ...

class BasicResponse(_message.Message):
    __slots__ = ["error_message", "success"]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error_message: str
    success: bool
    def __init__(self, success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class BlankRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Credentials(_message.Message):
    __slots__ = ["user_id"]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class FlushResponse(_message.Message):
    __slots__ = ["error_message", "queuedMessages", "success"]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    QUEUEDMESSAGES_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error_message: str
    queuedMessages: _containers.RepeatedCompositeFieldContainer[Message]
    success: bool
    def __init__(self, success: bool = ..., error_message: _Optional[str] = ..., queuedMessages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = ["wildcard"]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    wildcard: str
    def __init__(self, wildcard: _Optional[str] = ...) -> None: ...

class ListResponse(_message.Message):
    __slots__ = ["accounts", "error_message", "success"]
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[Account]
    error_message: str
    success: bool
    def __init__(self, success: bool = ..., error_message: _Optional[str] = ..., accounts: _Optional[_Iterable[_Union[Account, _Mapping]]] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ["author_id", "recipient_id", "text"]
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    author_id: str
    recipient_id: str
    text: str
    def __init__(self, author_id: _Optional[str] = ..., recipient_id: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...
