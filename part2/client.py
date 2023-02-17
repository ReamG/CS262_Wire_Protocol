import logging

import grpc
import schema_pb2 as schema
import schema_pb2_grpc as services

from concurrent.futures import ThreadPoolExecutor

# Helper function found here:
# https://stackoverflow.com/questions/39969064/how-to-print-a-message-box-in-python
def print_msg_box(msg, indent=1, width=None, title=None):
    """Print message-box with optional title."""
    chunk_size = 64
    msg.text = "Message: " + msg.text
    lines = [ "From: " + msg.author_id ] + [ msg.text[i:i+chunk_size] for i in range(0, len(msg.text), chunk_size) ]
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f'║{space}{title:<{width}}{space}║\n'  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += ''.join([f'║{space}{line:<{width}}{space}║\n' for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    print("\n" + box)

# Print an error string in red color
def print_error(msg):
    print("\033[91m{}\033[00m".format(msg))

# Print a success string in green color
def print_success(msg):
    print("\033[92m{}\033[00m".format(msg))

class Client:
    def __init__(self):
        self.executor = ThreadPoolExecutor()
        self.user_id = ""
        self.stub = None
    
    def is_logged_in(self):
        return len(self.user_id) > 0
    
    def watch_messages(self, resp_iter):
        try:
            for resp in resp_iter:
                print_msg_box(resp)
        except Exception as e:
            print_error("Error: Something has gone wrong. You may need to restart your client")
    
    def subscribe(self):
        if not self.is_logged_in():
            print_error("Error: Something has gone wrong. You may need to restart your client")
            return
        resp_iter = self.stub.Subscribe(schema.Credentials(user_id=self.user_id))
        self.executor.submit(self.watch_messages, resp_iter)

    def handle_create(self):
        if self.is_logged_in():
            print_error("You're already logged in as {}.".format(self.user_id))
            print_error("Restart the client to create a different account")
            return
        username = input("> Enter a username: ")
        if len(username) <= 0:
            print_error("Error: username cannot be empty")
            return
        resp = self.stub.Create(schema.Credentials(user_id=username))
        if not resp.success:
            print_error("Error: {}".format(resp.error_message))
            return
        print_success("Success! Account created")
        self.user_id = username
        self.subscribe()

    def handle_login(self):
        if self.is_logged_in():
            print_error("You're already logged in as {}.".format(self.user_id))
            print_error("Restart the client to login to a different account")
            return
        username = input("> Enter a username: ")
        if len(username) <= 0:
            print_error("Error: username cannot be empty")
            return
        resp = self.stub.Login(schema.Credentials(user_id=username))
        if not resp.success:
            print_error("Error: {}".format(resp.error_message))
            return
        print_success("Success! Logged in as {}".format(username))
        self.user_id = username
        self.subscribe()

    def handle_delete(self):
        if not self.is_logged_in():
            print("You must be logged in to delete an account")
            return
        verify = input("Are you sure you want to delete your account? (y/n): ")
        if not verify == "y":
            return
        resp = self.stub.Delete(schema.Credentials(user_id=self.user_id))
        if resp.success:
            print_success("Success! Account deleted")
            self.user_id = ""
        else:
            print_error("Error: {}".format(resp.error_message))

    def handle_list(self):
        wildcard = input("> Input a text filter: ")
        resp = self.stub.List(schema.ListRequest(wildcard=wildcard))
        if not resp.success:
            print_error("Error: {}".format(resp.error_message))
            return
        print("{} users matching '{}'".format(len(resp.accounts), wildcard))
        for user in resp.accounts:
            print(user.user_id)

    def handle_send(self):
        recipient = input("> Recipient id: ")
        if len(recipient) <= 0:
            print_error("Error: Recipient cannot be empty")
            return
        text = input("> What would you like to say?\n")
        resp = self.stub.Send(schema.Message(
            author_id=self.user_id,
            recipient_id=recipient,
            text=text
        ))
        if not resp.success:
            print_error("Error: {}".format(resp.error_message))
            return
        print_success("Success! Message sent")

    def parse_input(self, input_str):
        if input_str == "create":
            return self.handle_create
        elif input_str == "login":
            return self.handle_login
        elif input_str == "delete":
            return self.handle_delete
        elif input_str == "list":
            return self.handle_list
        elif input_str == "send":
            return self.handle_send
        else:
            print_error("Error: Invalid command")

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