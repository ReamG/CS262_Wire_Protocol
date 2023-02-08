import logging

import grpc
import schema_pb2
import schema_pb2_grpc

def handle_create(stub: schema_pb2_grpc.ChatHandlerStub):
    username = input("Enter a username: ")
    if len(username) <= 0:
        print("Error: username cannot be empty")
        return
    stub.Create(schema_pb2.Credentials(userId=username))

def handle_login(stub: schema_pb2_grpc.ChatHandlerStub):
    username = input("Enter a username: ")
    if len(username) <= 0:
        print("Error: username cannot be empty")
        return
    stub.Login(schema_pb2.Credentials(userId=username))

def parse_input(input_str):
    if input_str == "create":
        return handle_create
    if input_str == "login":
        return handle_login
    return None

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = schema_pb2_grpc.ChatHandlerStub(channel=channel)
        while True:
            raw_input = input("Enter a command: ")
            handler = parse_input(raw_input)
            if handler:
                handler(stub)


if __name__ == '__main__':
    logging.basicConfig()
    run()