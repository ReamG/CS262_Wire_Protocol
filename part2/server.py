# echo-server.py

from concurrent import futures

import grpc
import schema_pb2
import schema_pb2_grpc

users = []

msgs_cache = {}


class ChatHandlerServicer(object):
    """The main service
    """

    def Create(self, request, context):
        for user in users:
            if request.userId == user.userId:
                return  schema_pb2.BasicResponse(False, "userID already exists")
        
        new_account = schema_pb2.Account("request.userId",True)
        users.append(new_account)
        msgs_cache[new_account.userId] = []

        return schema_pb2.BasicResponse(True, "")
    
    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        for user in users:
            if request.userId == user.userId:
                user.isLoggedIn = True
                return schema_pb2.BasicResponse(True, "")
        return schema_pb2.BasicResponse(False, "UserId does not exist. Try creating an account.")

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        initial_len = len(users)
        users = [user for user in users if not request.userId == user.userId]
        final_len = len(users)
        
        if initial_len == final_len:
            return schema_pb2.BasicResponse(False, "UserId does not exist.")
        
        return schema_pb2.BasicResponse(True, "")

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

    def List(self, request, context):
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