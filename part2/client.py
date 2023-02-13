import logging

import grpc
import schema_pb2 as schema
import schema_pb2_grpc as services

class Client:
    def __init__(self):
        self.my_userId = ""
    
    def is_logged_in(self):
        return len(self.my_userId) > 0

    def handle_create(self, stub: services.ChatHandlerStub):
        if self.is_logged_in():
            print("You're already logged in as {}.".format(self.my_userId))
            print("Restart the client to create a different account")
            return
        username = input("Enter a username: ")
        if len(username) <= 0:
            print("Error: username cannot be empty")
            return
        resp = stub.Create(schema.Credentials(userId=username))
        if not resp.success:
            print("Error: {}".format(resp.errorMessage))
            return
        print("Success! Account created")
        self.my_userId = username

    def handle_login(self, stub: services.ChatHandlerStub):
        if self.is_logged_in():
            print("You're already logged in as {}.".format(self.my_userId))
            print("Restart the client to login to a different account")
            return
        username = input("Enter a username: ")
        if len(username) <= 0:
            print("Error: username cannot be empty")
            return
        resp = stub.Login(schema.Credentials(userId=username))
        if not resp.success:
            print("Error: {}".format(resp.errorMessage))
            return
        print("Success! Logged in as {}".format(username))
        self.my_userId = username

    def handle_delete(self, stub: services.ChatHandlerStub):
        if not self.is_logged_in():
            print("You must be logged in to delete an account")
            return
        verify = input("Are you sure you want to delete your account? (y/n): ")
        if not verify == "y":
            return
        resp = stub.Delete(schema.Credentials(userId=self.my_userId))
        if resp.success:
            print("Success! Account deleted")
            self.my_userId = ""
        else:
            print("Error: {}".format(resp.errorMessage))

    def handle_list(self, stub: services.ChatHandlerStub):
        wildcard = input("Input a text filter: ")
        resp = stub.List(schema.ListRequest(wildcard=wildcard))
        if not resp.success:
            print("Error: {}".format(resp.errorMessage))
            return
        print("{} users matching '{}'".format(len(resp.accounts), wildcard))
        for user in resp.accounts:
            print(user.userId)

    def handle_send(self, stub: services.ChatHandlerStub):
        pass

    def parse_input(self, input_str):
        if input_str == "create":
            return self.handle_create
        if input_str == "login":
            return self.handle_login
        if input_str == "delete":
            return self.handle_delete
        if input_str == "list":
            return self.handle_list
        if input_str == "send":
            return self.handle_send
        return None

    def run(self):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = services.ChatHandlerStub(channel=channel)
            while True:
                raw_input = input("> Enter a command: ")
                handler = self.parse_input(raw_input)
                if handler:
                    handler(stub)

if __name__ == '__main__':
    logging.basicConfig()
    instance = Client()
    instance.run()