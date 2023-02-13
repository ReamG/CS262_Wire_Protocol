import logging

import grpc
import schema_pb2 as schema
import schema_pb2_grpc as services

from concurrent.futures import ThreadPoolExecutor
import threading

# Helper function found here:
# https://stackoverflow.com/questions/39969064/how-to-print-a-message-box-in-python
def print_msg_box(msg, indent=1, width=None, title=None):
    """Print message-box with optional title."""
    chunk_size = 64
    msg.text = "Message: " + msg.text
    lines = [ "From: " + msg.authorId ] + [ msg.text[i:i+chunk_size] for i in range(0, len(msg.text), chunk_size) ]
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f'║{space}{title:<{width}}{space}║\n'  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    erase = '\x1b[1A\x1b[0G\x1b[2K'
    num_erase = box.count("\n") + 2
    print(erase * num_erase + "\n" + box + "\x1b[1E\x1b[1D]")

class Client:
    def __init__(self):
        self.executor = ThreadPoolExecutor()
        self.userId = ""
        self.stub = None
    
    def is_logged_in(self):
        return len(self.userId) > 0
    
    def watch_messages(self, resp_iter):
        try:
            for resp in resp_iter:
                print_msg_box(resp)
        except Exception as e:
            print("Error: Something has gone wrong. You may need to restart your client")
    
    def subscribe(self):
        if not self.is_logged_in():
            print("Error: Something has gone wrong. You may need to restart your client")
            return
        resp_iter = self.stub.Subscribe(schema.Credentials(userId=self.userId))
        self.executor.submit(self.watch_messages, resp_iter)

    def handle_create(self):
        if self.is_logged_in():
            print("You're already logged in as {}.".format(self.userId))
            print("Restart the client to create a different account")
            return
        username = input("> Enter a username: ")
        if len(username) <= 0:
            print("Error: username cannot be empty")
            return
        resp = self.stub.Create(schema.Credentials(userId=username))
        if not resp.success:
            print("Error: {}".format(resp.errorMessage))
            return
        print("Success! Account created")
        self.userId = username
        self.subscribe()

    def handle_login(self):
        if self.is_logged_in():
            print("You're already logged in as {}.".format(self.userId))
            print("Restart the client to login to a different account")
            return
        username = input("> Enter a username: ")
        if len(username) <= 0:
            print("Error: username cannot be empty")
            return
        resp = self.stub.Login(schema.Credentials(userId=username))
        if not resp.success:
            print("Error: {}".format(resp.errorMessage))
            return
        print("Success! Logged in as {}".format(username))
        self.userId = username
        self.subscribe()

    def handle_delete(self):
        if not self.is_logged_in():
            print("You must be logged in to delete an account")
            return
        verify = input("Are you sure you want to delete your account? (y/n): ")
        if not verify == "y":
            return
        resp = self.stub.Delete(schema.Credentials(userId=self.userId))
        if resp.success:
            print("Success! Account deleted")
            self.userId = ""
        else:
            print("Error: {}".format(resp.errorMessage))

    def handle_list(self):
        wildcard = input("> Input a text filter: ")
        resp = self.stub.List(schema.ListRequest(wildcard=wildcard))
        if not resp.success:
            print("Error: {}".format(resp.errorMessage))
            return
        print("{} users matching '{}'".format(len(resp.accounts), wildcard))
        for user in resp.accounts:
            print(user.userId)

    def handle_send(self):
        recipient = input("> Recipient id: ")
        if len(recipient) <= 0:
            print("Error: Recipient cannot be empty")
            return
        text = input("> What would you like to say?\n")
        resp = self.stub.Send(schema.Message(
            authorId=self.userId,
            recipientId=recipient,
            text=text
        ))
        if not resp.success:
            print("Error: {}".format(resp.errorMessage))
            return
        print("Success! Message sent")

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
            self.stub = services.ChatHandlerStub(channel=channel)
            while True:
                raw_input = input("> Enter a command: ")
                handler = self.parse_input(raw_input)
                if handler:
                    handler()

if __name__ == '__main__':
    logging.basicConfig()
    instance = Client()
    instance.run()