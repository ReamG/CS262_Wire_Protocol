# echo-server.py

from threading import Event
from concurrent import futures

import grpc
import schema_pb2 as schema
import schema_pb2_grpc as services
import time
import pdb

class ChatHandlerServicer(object):
    """The main service
    """

    def __init__(self, executor):
        self.executor = executor
        self.users = {}
        self.msgs_cache = {}
        self.user_events = {}

    def Create(self, request, context):
        for user_id in self.users:
            if request.user_id == user_id:
                return  schema.BasicResponse(success=False, error_message="user_id already exists")
        new_account = schema.Account(user_id=request.user_id, is_logged_in=False)
        self.users[new_account.user_id] = new_account
        self.msgs_cache[new_account.user_id] = []
        self.user_events[new_account.user_id] = Event()
        return schema.BasicResponse(success=True, error_message="")
    
    def Login(self, request, context):
        if request.user_id in self.users:
            return schema.BasicResponse(success=True, error_message="")
        return schema.BasicResponse(success=False, error_message="user_id does not exist. Try creating an account.")
    
    def List(self, request, context):
        satisfying = filter(lambda user : request.wildcard in user.user_id, self.users.values())
        return schema.ListResponse(success=True, accounts=satisfying)

    def Delete(self, request, context):
        initial_len = len(self.users)
        self.users = [user for user in self.users if not request.user_id == user.user_id]
        final_len = len(self.users)
        
        if initial_len == final_len:
            return schema.BasicResponse(success=False, error_message="user_id does not exist.")
        
        return schema.BasicResponse(success=True, error_message="")
    
    def Subscribe(self, request, context):
        def log_out():
            self.users[request.user_id].is_logged_in = False
            self.user_events[request.user_id].set()
        
        context.add_callback(log_out)
        self.users[request.user_id].is_logged_in = True

        while self.users[request.user_id].is_logged_in:
            try:
                self.user_events[request.user_id].wait()
                self.user_events[request.user_id].clear()
                while len(self.msgs_cache[request.user_id]) > 0:
                    yield self.msgs_cache[request.user_id][0]
                    self.msgs_cache[request.user_id] = self.msgs_cache[request.user_id][1:]
            except Exception as e:
                self.users[request.user_id].is_logged_in = False
                self.user_events[request.user_id].clear()
                break

    def Send(self, request, context):
        if not request.recipient_id in self.msgs_cache:
            return schema.BasicResponse(success=False, error_message="Recipient does not exist")
        if not request.author_id in self.msgs_cache:
            return schema.BasicResponse(success=False, error_message="Author does not exist")
        
        self.msgs_cache[request.recipient_id].append(request)
        self.user_events[request.recipient_id].set()
        return schema.BasicResponse(success=True, error_message="")

    def Flush(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

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