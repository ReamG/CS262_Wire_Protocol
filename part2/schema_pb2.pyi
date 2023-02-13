from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Account(_message.Message):
    __slots__ = ["isLoggedIn", "userId"]
    ISLOGGEDIN_FIELD_NUMBER: _ClassVar[int]
    USERID_FIELD_NUMBER: _ClassVar[int]
    isLoggedIn: bool
    userId: str
    def __init__(self, userId: _Optional[str] = ..., isLoggedIn: bool = ...) -> None: ...

class BasicResponse(_message.Message):
    __slots__ = ["errorMessage", "success"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    errorMessage: str
    success: bool
    def __init__(self, success: bool = ..., errorMessage: _Optional[str] = ...) -> None: ...

class BlankRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Credentials(_message.Message):
    __slots__ = ["userId"]
    USERID_FIELD_NUMBER: _ClassVar[int]
    userId: str
    def __init__(self, userId: _Optional[str] = ...) -> None: ...

class FlushResponse(_message.Message):
    __slots__ = ["errorMessage", "queuedMessages", "success"]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    QUEUEDMESSAGES_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    errorMessage: str
    queuedMessages: _containers.RepeatedCompositeFieldContainer[Message]
    success: bool
    def __init__(self, success: bool = ..., errorMessage: _Optional[str] = ..., queuedMessages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = ["wildcard"]
    WILDCARD_FIELD_NUMBER: _ClassVar[int]
    wildcard: str
    def __init__(self, wildcard: _Optional[str] = ...) -> None: ...

class ListResponse(_message.Message):
    __slots__ = ["accounts", "errorMessage", "success"]
    ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    ERRORMESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    accounts: _containers.RepeatedCompositeFieldContainer[Account]
    errorMessage: str
    success: bool
    def __init__(self, success: bool = ..., errorMessage: _Optional[str] = ..., accounts: _Optional[_Iterable[_Union[Account, _Mapping]]] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ["authorId", "recipientId", "text"]
    AUTHORID_FIELD_NUMBER: _ClassVar[int]
    RECIPIENTID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    authorId: str
    recipientId: str
    text: str
    def __init__(self, authorId: _Optional[str] = ..., recipientId: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...
