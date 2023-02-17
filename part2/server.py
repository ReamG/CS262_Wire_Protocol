# echo-server.py

from threading import Event
from concurrent import futures

import grpc
import schema_pb2 as schema
import schema_pb2_grpc as services
import time

class ChatHandlerServicer(object):
    """The main service
    """

    def __init__(self, executor):
        self.executor = executor
        self.users = {}
        self.msgs_cache = {}
        self.user_events = {}

    def Create(self, request, context):
        for userId in self.users():
            if request.userId == userId:
                return  schema.BasicResponse(success=False, errorMessage="userID already exists")
        new_account = schema.Account(userId=request.userId, isLoggedIn=False)
        self.users[new_account.userId] = new_account
        self.msgs_cache[new_account.userId] = []
        self.user_events[new_account.userId] = Event()
        return schema.BasicResponse(success=True, errorMessage="")
    
    def Login(self, request, context):
        if request.userId in self.users:
            return schema.BasicResponse(success=True, errorMessage="")
        return schema.BasicResponse(success=False, errorMessage="UserId does not exist. Try creating an account.")
    
    def List(self, request, context):
        satisfying = filter(lambda user : request.wildcard in user.userId, self.users)
        return schema.ListResponse(success=True, accounts=satisfying)

    def Delete(self, request, context):
        initial_len = len(self.users)
        self.users = [user for user in self.users if not request.userId == user.userId]
        final_len = len(self.users)
        
        if initial_len == final_len:
            return schema.BasicResponse(success=False, errorMessage="UserId does not exist.")
        
        return schema.BasicResponse(success=True, errorMessage="")
    
    def Subscribe(self, request, context):
        def log_out():
            self.users[request.userId].isLoggedIn = False
            self.user_events[request.userId].set()
        
        context.add_callback(log_out)
        self.users[request.userId].isLoggedIn = True

        while self.users[request.userId].isLoggedIn:
            try:
                self.user_events[request.userId].wait()
                self.user_events[request.userId].clear()
                if len(self.msgs_cache[request.userId]) > 0:
                    yield self.msgs_cache[request.userId][0]
                    self.msgs_cache[request.userId] = self.msgs_cache[request.userId][1:]
            except Exception as e:
                self.users[request.userId].isLoggedIn = False
                self.user_events[request.userId].clear()
                break

    def Send(self, request, context):
        if not request.recipientId in self.msgs_cache:
            return schema.BasicResponse(success=False, errorMessage="Recipient does not exist")
        if not request.authorId in self.msgs_cache:
            return schema.BasicResponse(success=False, errorMessage="Author does not exist")
        self.msgs_cache[request.recipientId].append(request)
        self.user_events[request.recipientId].set()
        return schema.BasicResponse(success=True, errorMessage="")

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