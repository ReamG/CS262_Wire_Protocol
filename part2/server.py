# echo-server.py

from concurrent import futures

import grpc
import schema_pb2
import schema_pb2_grpc

class ChatHandlerServicer(object):
    """The main service
    """

    def __init__(self):
        self.users = []
        self.msgs_cache = {}

    def Create(self, request, context):
        for user in self.users:
            if request.userId == user.userId:
                return  schema_pb2.BasicResponse(success=False, errorMessage="userID already exists")
        new_account = schema_pb2.Account(userId=request.userId,isLoggedIn=True)
        self.users.append(new_account)
        self.msgs_cache[new_account.userId] = []
        return schema_pb2.BasicResponse(success=True, errorMessage="")
    
    def Login(self, request, context):
        for user in self.users:
            if request.userId == user.userId:
                user.isLoggedIn = True
                return schema_pb2.BasicResponse(success=True, errorMessage="")
        return schema_pb2.BasicResponse(success=False, errorMessage="UserId does not exist. Try creating an account.")
    
    def List(self, request, context):
        satisfying = filter(lambda user : request.wildcard in user.userId, self.users)
        return schema_pb2.ListResponse(success=True, accounts=satisfying)

    def Delete(self, request, context):
        initial_len = len(self.users)
        self.users = [user for user in self.users if not request.userId == user.userId]
        final_len = len(self.users)
        
        if initial_len == final_len:
            return schema_pb2.BasicResponse(success=False, errorMessage="UserId does not exist.")
        
        return schema_pb2.BasicResponse(success=True, errorMessage="")

    def Send(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Flush(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schema_pb2_grpc.add_ChatHandlerServicer_to_server(
        ChatHandlerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()