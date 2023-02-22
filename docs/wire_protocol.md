# Wire Protocol

This document outlines the wire protocol we used to define the features listed in `implementation.md`. We include snippets of code from part one and part two, and note the differences between them.

## High Level Overview

- [Requests](#requests)
  - [Request Operations](#request-operations)
  - [Unmarshalling Requests](#unmarshalling-requests)
- [Responses](#responses)
  - [Response Types](#response-types)
  - [Unmarshalling Responses](#unmarshalling-responses)

## Requests

Requests from the client to the server are at most 1024 bytes long and must start with the following 10 bytes:

`[ version - 1 byte, user_id - 8 bytes, op_code - 1 byte ]`

- `version` is the version of the app we are running. For our purposes this is always `0`, but in principal it could change and be used to deprecate/add features later.
- `user_id` is the user_id of the user making the request, OR in the case of login / create the user who is attempting to authenticate. **NOTE: This immediately implies that we've capped usernames to 8 characters (which is true) for simplicity**. We let usernames contain any charactes EXCEPT commas.
- `op_code` is the operation that we want to perform on the server. See the below operations section for the possible values of the code and specifics about their implementation.

You can get a sense of the high level operation mapping by looking at the top of `coding.py`.

```
VERSION = "0"

ERROR_MESSAGE_LENGTH = 64
MAX_MESSAGE_LENGTH = 280

OP_TO_CODE_MAP = {
    "create": "1",
    "login": "2",
    "delete": "3",
    "get": "4",
    "send": "5",
    "list": "6",
}

CODE_TO_OP_MAP = {
    "1": "create",
    "2": "login",
    "3": "delete",
    "4": "get",
    "5": "send",
    "6": "list",
}
```

Note as well the following helper functions in `coding.py` which allow us to ensure that each of these fields (ex: user*id) is \_exactly* as long as it's supposed to be, no shorter, no longer:

```
def pad_to_length(s, length):
    """
    Pads a string to a given length
    NOTE: if len(s) > length, this will truncate the string
    """
    if len(s) > length:
        return s[:length]
    return s + (length - len(s)) * "\0"

def unpad(s):
    """
    Removes padding from a string
    """
    return s.strip("\0")
```

The below code implements the base request.

```
class Request:
    """
    A base class for all requests from client -> server
    """
    def __init__(self, user_id):
        self.user_id = user_id
```

You may notice that it appears to be missing `op_code` and `version`. Don't worry, since in our case version was alays fixed, we handled this in the marshalling functions. To handle the opcode, we created different marshalling functions that would automatically add the correct opcode. Other more complicated requests extend this base class, which we cover later.

For part two we don't send a user_id along with each request. Thus our base request(s) are simply

```
message BlankRequest { }
message Credentials {
  string user_id = 1;
}
```

### Request Operations

`op_code 1 = create`. Attempts to create an account with the username stored in `user_id`. Marshalling function:

```
def marshal_create_request(req: Request):
    """
    Marshals a create Request into a byte string
    """
    return "{}{}{}".format(
        VERSION,
        pad_to_length(req.user_id, 8),
        OP_TO_CODE_MAP["create"],
    ).encode()
```

For part two create uses `message Credentials {
  string user_id = 1;
}` described above to pass this information, and calls the relevant create function on the stub (talked about more in the responses section).

`op_code 2 = login`. Attempts to log in to the account with the username stored in `user_id`. Marshalling function:

```
def marshal_login_request(req: Request):
    """
    Marshals a login Request into a byte string
    """
    return "{}{}{}".format(
        VERSION,
        pad_to_length(req.user_id, 8),
        OP_TO_CODE_MAP["login"],
    ).encode()
```

Similar to create in part two we use `message Credentials {
  string user_id = 1;
}` instead.

`op_code 3 = delete`. Deletes the account with the username stored in `user_id`. Note that in theory our implementation could be used to delete arbitrary accounts, but we chose to simplify it and restrict the client to only ever issue such delete requests with their own `user_id`.

```
def marshal_delete_request(req: Request):
    """
    Marshals a delete Request into a byte string
    """
    return "{}{}{}".format(
        VERSION,
        pad_to_length(req.user_id, 8),
        OP_TO_CODE_MAP["delete"],
    ).encode()
```

Similar to create and log in in part two we use `message Credentials {
  string user_id = 1;
}` instead.

(P.S. Before we go any further, you may be wondering why we split all these marshalling functions up instead of just maping the op a parameter. In our experience, we made this decision to increase readability of the client and server code. So while yes, the helper functions do seem a bit repetitive, when it comes to using them it makes the "interesting" code much more readable.)

`op_code 4 = get`. This asks the server the question, "do I have any unread messages?" If the answer is yes, exactly one is returned. If the answer is no, a message with status `success=False` is returned to indicate there are no unread messages.

- NOTE: Our solution in part one achieves (near) instantaneous delivery by polling. Clients issue a `get` request to the server once a second (more detail on this later). In part two, the added simplicity of gRPC allowed us to make a more complicated solution using blocking. Where threads are awoken exactly when there is a message. Thus, this operation is present in part one but NOT in part two.

Marshalling function

```
def marshal_get_request(req: Request):
    """
    Marshals a subscribe Request into a byte string
    """
    return "{}{}{}".format(
        VERSION,
        pad_to_length(req.user_id, 8),
        OP_TO_CODE_MAP["get"],
    ).encode()
```

As mentioned above, in part two the added simplicity lets us achieve a non-polling solution, so this request type becomes unnecessary.

`op_code 5 = send`. This is the first place where we get more complicated than the basic request. The protocol extends the basic definition with the following:

`[ version - 1 byte, user_id - 8 bytes, op_code - 1 byte, recipient_id - 8 bytes, text - 280 bytes ]`

Again, we always pad/unpad values when marshalling/unmarshalling to know that these fieds are _always_ 8 or 280 bytes. The extended request class is

```
class SendRequest(Request):
    """
    A request to send a message to a user
    """
    def __init__(self, user_id, recipient_id, text):
        super().__init__(user_id)
        self.recipient_id = recipient_id
        self.text = text
```

and the marshalling function works

```
def marshal_send_request(req: SendRequest):
    """
    Marshals a send Request into a byte string
    """
    return "{}{}{}{}{}".format(
        VERSION,
        pad_to_length(req.user_id, 8),
        OP_TO_CODE_MAP["send"],
        pad_to_length(req.recipient_id, 8),
        pad_to_length(req.text, MAX_MESSAGE_LENGTH),
    ).encode()
```

In part two, we replace this with the following message:

```
// Used for sending a message
message Message {
  string author_id = 1;
  string recipient_id = 2;
  string text = 3;
}
```

It's very similar, but note that semantically `user_id` is no longer part of every request, so we must also have an `author_id` field to store the author.

`op_code 6 = list`. This is used to get all the accounts that exist on the server matching a given wildcard. It extends the basic request in the following way:

`[ version - 1 byte, user_id - 8 bytes, op_code - 1 byte, wildcard - 8 bytes, page - 8 bytes ]`

For simplicity, we use a page size of 4 accounts on the back-end. This, combined with the fact that the max page value we can pass is `99999999` means we _technically_ can only support ~400 million accounts, but this should be plenty. The corresponding request object is

```
class ListRequest(Request):
    """
    A request to list all messages that match a wildcard
    """
    def __init__(self, user_id, wildcard, page):
        super().__init__(user_id)
        self.wildcard = wildcard
        self.page = page
```

and marshalling function

```
def marshal_list_request(req: ListRequest):
    """
    Marshals a list Request into a byte string
    """
    return "{}{}{}{}{}".format(
        VERSION,
        pad_to_length(req.user_id, 8),
        OP_TO_CODE_MAP["list"],
        pad_to_length(req.wildcard, 8),
        pad_to_length(str(req.page), 8),
    ).encode()
```

In part two we use

```
message ListRequest {
  string wildcard = 1;
}
```

Note that because gRPC supports arbitrary length lists, we can remove the pagination requirement, allowing a slightly better user experience.

### Unmarshalling Requests

When the server receives a request from the client, it is unmarshaled using the following function:

```
def unmarshal_request(data: bytes):
    """
    Unmarshals a byte string into a Request
    """
    data = data.decode()
    version = data[0]
    user_id = unpad(data[1:9])
    op_code = data[9]
    op = CODE_TO_OP_MAP[op_code]
    if op == "create":
        return Request(user_id), op
    elif op == "login":
        return Request(user_id), op
    elif op == "delete":
        return Request(user_id), op
    elif op == "list":
        wildcard = unpad(data[10:18])
        page = unpad(data[18:26])
        page_num = int(page)
        return ListRequest(user_id, wildcard, page_num), op
    elif op == "get":
        return Request(user_id), op
    elif op == "send":
        recipient_id = unpad(data[10:18])
        text = unpad(data[18:18+MAX_MESSAGE_LENGTH])
        return SendRequest(user_id, recipient_id=recipient_id, text=text), op
    else:
        raise Exception("Unknown op code: {}".format(op_code))
```

Again while this perhaps slightly more verbose than it needs to be, the added text aids in readability.

## Responses

Responses from the server to the client are at most 1024 bytes long and must start with the following 75 bytes:

`[ version - 1 byte, user_id - 8 bytes, resp_code - 1 byte, success - 1 byte, error_message - 64 byes ]`.

- `version` again, the version. We only use zero.
- `user_id` the user that issued the request leading to this response.
- `resp_code` a number telling us what kind of response this is
- `success` was the server successful
- `error_message` if the server was not successful, a message to the user telling them what went wrong.

The classes implementing responses are in `schema.py`. The base class is

```
class Response:
    """
    A base class for all responses from server -> client
    """
    def __init__(self, user_id, success, error_message):
        self.user_id = user_id
        self.success = success
        self.error_message = error_message
        self.type = "basic"
```

### Response Types

`resp_code 1 = basic`. A basic response. Used to respond to create, login, send, delete. The user only needs to know whether or not what they wanted succeeded. Marshalled by the following function in coding.py:

```
def marshal_response(resp: Response):
    """
    Marshals a Response into a byte string
    """
    return "{}{}{}{}{}".format(
        VERSION,
        pad_to_length(resp.user_id, 8),
        RESP_TO_CODE_MAP[resp.type],
        1 if resp.success else 0,
        pad_to_length(resp.error_message, ERROR_MESSAGE_LENGTH),
    ).encode()
```

In part two, we encapsulate this behavior using

```
message BasicResponse {
  bool success = 1;
  string error_message = 2;
}
```

We can now see the following broadstrokes services defined by part two:

```
service ChatHandler {
    rpc Create(Credentials) returns (BasicResponse);
    rpc Login(Credentials) returns (BasicResponse);
    rpc Delete(Credentials) returns (BasicResponse);
    rpc Subscribe(Credentials) returns (stream Message);
    rpc Send(Message) returns (BasicResponse);
}
```

Note the subscribe function, which plays the role of `get` from part one. The only difference is it blocks instead of polling, so is likely less taxing on the server.

`resp_code 2 = list`. A response containing a list of users. We simply pass this as a string with comma separated users.

```
def prep_accounts(accounts):
    """
    Turns a list of accounts into a string
    """
    as_strings = [account.user_id for account in accounts]
    return ",".join(as_strings)

def post_accounts(str):
    """
    Turns a string of accounts into a list
    """
    if str == "":
        return []
    return str.split(",")
```

This is why we had to restrict commas from usernames earlier. The class in `schema.py` that extends the basic response to implement this is:

```
class ListResponse(Response):
    """
    A response to a ListRequest
    """
    def __init__(self, user_id, success, error_message, accounts):
        super().__init__(user_id, success, error_message)
        self.accounts = accounts
        self.type = "list"
```

and mashalling in `coding.py` looks like

```
def marshal_list_response(resp: ListResponse):
    """
    Marshals a ListResponse into a byte string
    """
    return "{}{}{}{}{}{}".format(
        VERSION,
        pad_to_length(resp.user_id, 8),
        RESP_TO_CODE_MAP[resp.type],
        1 if resp.success else 0,
        pad_to_length(resp.error_message, ERROR_MESSAGE_LENGTH),
        prep_accounts(resp.accounts)
    ).encode()
```

Note that in part 2, gRPC can handle arbitrary lengths, and arrays that aren't strings. So we can simplify this a fair amount by using the message

```
message ListResponse {
  bool success = 1;
  string error_message = 2;
  repeated Account accounts = 3;
}
```

and service

```
    ...
    rpc List(ListRequest) returns (ListResponse);
}
```

`resp_type 3 = message`. This is used to return a message to the user.

The corresponding schema is

```
class Message:
    """
    A class for messages sent from server -> client
    """
    def __init__(self, author_id, recipient_id, text, success):
        self.author_id = author_id
        self.recipient_id = recipient_id
        self.text = text
        self.success = success
```

and marshalling function in `coding.py` is

```
def marshal_message_response(msg: Message):
    """
    Marshals a Message into a byte string
    """
    return "{}{}{}{}{}{}{}".format(
        VERSION,
        pad_to_length(msg.recipient_id, 8),
        RESP_TO_CODE_MAP["message"],
        1 if msg.success else 0,
        pad_to_length("", ERROR_MESSAGE_LENGTH),
        pad_to_length(msg.author_id, 8),
        pad_to_length(msg.text, 280),
    ).encode()
```

It's a slight quirk of the polling method that the `error_message` field goes unused, and if something were to go wrong it would end up in the text field.

In gRPC, we get the added benefit that the

```
message Message {
  string author_id = 1;
  string recipient_id = 2;
  string text = 3;
}
```

we defined earlier can be reused as the response type, since in part two we implement blocking so we never need to send a `Message` with a status `false` to indicate that in fact no messages for the selected user exist.

### Unmarshalling Responses

The following (relatively straightforward) functions in `coding.py` unmarshals the responses:

```
def prep_accounts(accounts):
    """
    Turns a list of accounts into a string
    """
    as_strings = [account.user_id for account in accounts]
    return ",".join(as_strings)

def post_accounts(str):
    """
    Turns a string of accounts into a list
    """
    if str == "":
        return []
    return str.split(",")

def unmarshal_response(data):
    """
    Unmarshals a byte string into a Response
    """
    data = data.decode()
    version = data[0]
    user_id = unpad(data[1:9])
    resp_code = data[9]
    resp_type = CODE_TO_RESP_MAP[resp_code]
    success = data[10] == "1"
    error_message = unpad(data[11:11+ERROR_MESSAGE_LENGTH])
    if resp_type == "basic":
        return Response(user_id=user_id, success=success, error_message=error_message)
    elif resp_type == "list":
        accounts = post_accounts(data[11+ERROR_MESSAGE_LENGTH:])
        return ListResponse(user_id=user_id, success=success, error_message=error_message, accounts=accounts)
    elif resp_type == "message":
        author_id = unpad(data[11+ERROR_MESSAGE_LENGTH:11+ERROR_MESSAGE_LENGTH+8])
        text = unpad(data[11+ERROR_MESSAGE_LENGTH+8:])
        return Message(recipient_id=user_id, author_id=author_id, text=text, success=success)
    else:
        raise Exception("Unknown response type: {}".format(resp_type))
```

Again, we take advantage of the fact that our designed protocol always has fixed lengths for everything and pads to that length to make this process much simpler.
