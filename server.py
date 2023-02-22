# echo-server.py

import socket
from concurrent import futures

import schema
import coding

import time
import pdb

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

class Server:
    """
    A bare-bones server that listens for connections on a given host and port
    """

    def __init__(self, host, port, executor):
        """
        Initialize the server
        """
        self.host = host
        self.port = port
        self.executor = executor
        self.users = {}
        self.msgs_cache = {}
        self.user_events = {}
        self.ACCOUNT_PAGE_SIZE = 4
        self.alive = True
    
    def handle_create(self, request):
        """
        Creates a new account. Fails if the user_id already exists.
        """
        if request.user_id in self.users:
            return schema.Response(user_id=request.user_id, success=False, error_message="User already exists")
        new_account = schema.Account(user_id=request.user_id, is_logged_in=True)
        self.users[new_account.user_id] = new_account
        self.msgs_cache[new_account.user_id] = []
        return schema.Response(user_id=request.user_id, success=True, error_message="")
    
    def handle_login(self, request):
        """
        Logs in an existing account. Fails if the user_id does not exist or
        if the user is already logged in.
        """
        if not request.user_id in self.users:
            return schema.Response(user_id=request.user_id, success=False, error_message="User does not exist")
        if self.users[request.user_id].is_logged_in:
            return schema.Response(user_id=request.user_id, success=False, error_message="User already logged in")
        self.users[request.user_id].is_logged_in = True
        return schema.Response(user_id=request.user_id, success=True, error_message="")
    
    def handle_delete(self, request):
        """
        Deletes an existing account. Fails if the user_id does not exist.
        """
        if not request.user_id in self.users:
            return schema.Response(user_id=request.user_id, success=False, error_message="User does not exist")
        del self.users[request.user_id]
        del self.msgs_cache[request.user_id]
        return schema.Response(user_id=request.user_id, success=True, error_message="")
    
    def handle_list(self, request):
        """
        Lists all accounts that match the given wildcard.
        NOTE: "" will match all accounts. Other strings will simply use
        Python's built-in "in" operator.
        """
        satisfying = filter(lambda user : request.wildcard in user.user_id, self.users.values())
        limited_to_page = list(satisfying)[request.page * self.ACCOUNT_PAGE_SIZE : (request.page + 1) * self.ACCOUNT_PAGE_SIZE]
        return schema.ListResponse(user_id=request.user_id, success=True, error_message="", accounts=limited_to_page)
    
    def handle_subscribe(self, request, conn):
        """
        Turns this thread into one that sits and waits for messages to 
        pass on to the client.
        """
        if not request.user_id in self.users:
            # Inform the client that the subscription wasn't successful
            error_resp = schema.Response(user_id=request.user_id, success=False, error_message="User does not exist")
            message = coding.marshal_response(error_resp)
            conn.sendall(message)
            return
        
        # Inform the client that the subscription was successful
        success_resp = schema.Response(user_id=request.user_id, success=True, error_message="")
        message = coding.marshal_response(success_resp)
        conn.sendall(message)

        while True:
            if not self.alive:
                break
            if len(self.msgs_cache[request.user_id]) > 0:
                # Confirm that the client is stil there
                try:
                    health_message = coding.marshal_health_request(schema.Request(request.user_id))
                    conn.sendall(health_message)
                    data = conn.recv(1024)
                    if not data:
                        raise Exception("Client closed connection")
                except:
                    raise Exception("Client closed connection")
                message_obj = self.msgs_cache[request.user_id][0]
                self.msgs_cache[request.user_id] = self.msgs_cache[request.user_id][1:]
                message = coding.marshal_message_response(message_obj)
                conn.sendall(message)
            time.sleep(1)
    
    def handle_send(self, request):
        """
        Sends a message to the given user. If the user does not exist, return
        an error.
        """
        if not request.recipient_id in self.users:
            return schema.Response(user_id=request.user_id, success=False, error_message="User does not exist")
        message = schema.Message(author_id=request.user_id, recipient_id=request.recipient_id, text=request.text)
        self.msgs_cache[request.recipient_id].append(message)
        return schema.Response(user_id=request.user_id, success=True, error_message="")
    
    def handle_request_with_op(self, request, op):
        """
        Just does the dirty work of matching the code to the handler func
        """
        if op == "create":
            return self.handle_create(request)
        if op == "login":
            return self.handle_login(request)
        if op == "delete":
            return self.handle_delete(request)
        if op == "list":
            return self.handle_list(request)
        if op == "send":
            return self.handle_send(request)
        if op == "health":
            return schema.Response(user_id=request.user_id, success=True, error_message="")
        return None
    
    def handle_connection(self, conn, addr):
        print("New connection")
        user_id = ""
        while True:
            if not self.alive:
                break
            # Continue to receive data until the connection is closed
            try:
                data = conn.recv(1024)
                if not self.alive:
                    break
                if not data:
                    raise Exception("Client closed connection")
                request, op = coding.unmarshal_request(data)
                if op == "subscribe":
                    self.handle_subscribe(request, conn)
                    break
                resp = self.handle_request_with_op(request, op)
                if (op == "create" or op == "login") and resp.success:
                    user_id = request.user_id
                # Send back using the right encoding
                if op == "list":
                    data = coding.marshal_list_response(resp)
                else:
                    data = coding.marshal_response(resp)
                try:
                    conn.sendall(data)
                except:
                    raise Exception("Client closed connection")
            except Exception as e:
                if (e.args[0] == "Client closed connection"):
                    print(e.args[0])
                    if len(user_id) > 0:
                        self.users[user_id].is_logged_in = False
                    break
                else:
                    print("Error:", e.args[0])
                    resp = schema.Response(user_id=user_id, success=False, error_message=e.args[0])
                    data = coding.marshal_response(resp)
                    try:
                        conn.sendall(data)
                    except:
                        if len(user_id) > 0:
                            self.users[user_id].is_logged_in = False
                        break
        conn.close()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            while True:
                if not self.alive:
                    break
                conn, addr = s.accept()
                self.executor.submit(self.handle_connection, conn, addr)

if __name__ == "__main__":
    try:
        executor = futures.ThreadPoolExecutor()
        server = Server(host=HOST, port=PORT, executor=executor)
        server.start()
    except KeyboardInterrupt:
        server.alive = False
        print("Shutting down server...")
