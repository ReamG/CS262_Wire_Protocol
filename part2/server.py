# echo-server.py

from threading import Event
from concurrent import futures

import grpc
import schema_pb2 as schema
import schema_pb2_grpc as services
import time
import pdb

class ChatHandlerServicer(object):
    """
    The service handler for the chat server.
    """

    def __init__(self, executor):
        """
        Initialize the service handler.
        """
        self.executor = executor
        self.users = {}
        self.msgs_cache = {}
        self.user_events = {}

    def Create(self, request, context):
        """
        Creates a new account. Fails if the user_id already exists.
        NOTE: This does not "log in" the user. That happens in the
        Subscribe method, which sets up necessary precautions for
        sudden disconnects.
        """
        if request.user_id in self.users:
            return  schema.BasicResponse(success=False, error_message="user_id already exists")
        new_account = schema.Account(user_id=request.user_id, is_logged_in=True)
        self.users[new_account.user_id] = new_account
        self.msgs_cache[new_account.user_id] = []
        self.user_events[new_account.user_id] = Event()
        return schema.BasicResponse(success=True, error_message="")
    
    def Login(self, request, context):
        """
        Logs in an existing account. Fails if the user_id does not exist or
        if the user is already logged in.
        """
        if request.user_id in self.users:
            if self.users[request.user_id].is_logged_in:
                return schema.BasicResponse(success=False, error_message="user_id already logged in")
            self.users[request.user_id].is_logged_in = True
            return schema.BasicResponse(success=True, error_message="")
        return schema.BasicResponse(success=False, error_message="user_id does not exist. Try creating an account.")
    
    def List(self, request, context):
        """
        Lists all accounts that match the given wildcard.
        NOTE: "" will match all accounts. Other strings will simply use
        Python's built-in "in" operator.
        """
        satisfying = filter(lambda user : request.wildcard in user.user_id, self.users.values())
        return schema.ListResponse(success=True, accounts=satisfying)

    def Delete(self, request, context):
        """
        Deletes an existing account. Fails if the user_id does not exist.
        """
        if not request.user_id in self.users:
            return schema.BasicResponse(success=False, error_message="user_id does not exist.")
        self.users[request.user_id].is_logged_in = False
        self.user_events[request.user_id].set()
        del self.users[request.user_id]
        del self.msgs_cache[request.user_id]
        del self.user_events[request.user_id]
        
        return schema.BasicResponse(success=True, error_message="")
    
    def Subscribe(self, request, context):
        """
        Spins up a blocking thread on the server that will send messages
        to the client as they arrive using "yield".
        NOTE: While technically "log" in may succeed for multiple users,
        we enforce that only one subscribe thread can be active at a time
        for a given user.
        """
        if not request.user_id in self.users:
            return schema.BasicResponse(success=False, error_message="user_id does not exist.")
        if not self.users[request.user_id].is_logged_in:
            raise Exception("Must be logged in to subscribe")

        # Helper function to clean up when a client disconnects
        def log_out():
            self.users[request.user_id].is_logged_in = False
            self.user_events[request.user_id].set()
        context.add_callback(log_out)

        # Block until there is a message, then yield it to client and repeat
        while self.users[request.user_id].is_logged_in:
            try:
                self.user_events[request.user_id].wait()
                self.user_events[request.user_id].clear()
                while len(self.msgs_cache[request.user_id]) > 0:
                    yield self.msgs_cache[request.user_id][0]
                    self.msgs_cache[request.user_id] = self.msgs_cache[request.user_id][1:]
            except:
                self.users[request.user_id].is_logged_in = False
                self.user_events[request.user_id].clear()
                break
        
        return schema.BasicResponse(success=False, error_message="subscription thread dying.")

    def Send(self, request, context):
        """
        Sends a message to a recipient. Fails if either the recipient or
        the author does not exist. Handles the actual sending of the data
        simply by adding it to the recipient's message cache. Then, either
        the subscribe thread handles delivery immediately, or the next
        time the recipient logs in/subscribes, they will receive the message.
        """
        if not request.recipient_id in self.msgs_cache:
            return schema.BasicResponse(success=False, error_message="Recipient does not exist")
        if not request.author_id in self.users:
            return schema.BasicResponse(success=False, error_message="Author does not exist")
        
        self.msgs_cache[request.recipient_id].append(request)
        self.user_events[request.recipient_id].set()
        return schema.BasicResponse(success=True, error_message="")

def serve():
    executor = futures.ThreadPoolExecutor()
    server = grpc.server(executor)
    services.add_ChatHandlerServicer_to_server(
        ChatHandlerServicer(executor), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()