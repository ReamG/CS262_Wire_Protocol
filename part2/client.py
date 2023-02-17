import logging

import grpc
import schema_pb2 as schema
import schema_pb2_grpc as services
import time
import pdb

from concurrent.futures import ThreadPoolExecutor

# Helper function found here:
# https://stackoverflow.com/questions/39969064/how-to-print-a-message-box-in-python
def print_msg_box(msg, indent=1, width=None, title=None):
    """
    Print message-box with optional title.
    """
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

def print_error(msg):
    """
    Print an error string in red color
    """
    print("\033[91m{}\033[00m".format(msg))

def print_success(msg):
    """
    Print a success string in green color
    """
    print("\033[92m{}\033[00m".format(msg))

def print_info(msg):
    """
    Print an info string in a blue color
    """
    print("\033[94m{}\033[00m".format(msg))

class Client:
    def __init__(self):
        """
        Initialize the client with a thread pool executor
        """
        self.executor = ThreadPoolExecutor()
        self.user_id = ""
        self.stub = None
        # To handle errors and the case where the server is down, we
        # keep this bool. It is set to True only in the `check_server_health`
        # function, and set to false anywhere a request fails. When the health
        # is not good, no requests are processed until a successful health check
        # occurs.
        self.server_alive = False
    
    def is_logged_in(self):
        """
        Helper function to check if the user is logged in
        NOTE: Intentionally simple application with no password,
        so this is indeed a correct proxy to status
        """
        return len(self.user_id) > 0
    
    def check_server_health(self):
        """
        Helper function to check if the server is up
        """
        try:
            self.stub.List(schema.ListRequest(wildcard=""))
            print_success("Connection to server is good")
            self.server_alive = True
        except:
            self.server_alive = False
    
    def watch_messages(self, resp_iter):
        """
        A function that will be run in a separate thread to watch for messages
        NOTE: Takes advantage of the ThreadPoolExecutor to run this function
        """
        try:
            for resp in resp_iter:
                print_msg_box(resp)
        except:
            print_error("Error: Something has gone wrong. You may need to restart your client")
            self.server_alive = False
            
    
    def subscribe(self):
        """
        Subscribe to the server to receive messages
        """
        if not self.is_logged_in():
            print_error("Error: Something has gone wrong. You may need to restart your client")
            self.server_alive = False
            return
        resp_iter = self.stub.Subscribe(schema.Credentials(user_id=self.user_id))
        self.executor.submit(self.watch_messages, resp_iter)

    def handle_create(self):
        """
        Fails if the user is already logged in, they submit an empty username,
        or if the creation fails in expected way.
        NOTE: Expected to be run inside a safety_wrap
        """
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
        """
        Fails if the user is already logged in, they submit an empty username,
        or if the login fails in expected way.
        NOTE: Expected to be run inside a safety_wrap
        """
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
        """
        Fails if the user is not logged in, they don't confirm the deletion,
        or if the deletion fails in expected way.
        NOTE: Expected to be run inside a safety_wrap
        """
        if not self.is_logged_in():
            print_error("Error: You must be logged in to delete an account")
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
        """
        Fails iff the request fails in expected way.
        NOTE: Expected to be run inside a safety_wrap
        """
        wildcard = input("> Input a text filter: ")
        resp = self.stub.List(schema.ListRequest(wildcard=wildcard))
        if not resp.success:
            print_error("Error: {}".format(resp.error_message))
            return
        print_info("{} users matching '{}'".format(len(resp.accounts), wildcard))
        for user in resp.accounts:
            print(user.user_id)

    def handle_send(self):
        """
        Fails if the user is not logged in, they submit an empty recipient,
        or if the send fails in expected way.
        NOTE: Expected to be run inside a safety_wrap
        """
        if not self.is_logged_in():
            print_error("Error: You must be logged in to send a message")
            return
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
    
    def safety_wrap(self, func):
        """
        Wraps a handler function in a try except block to handle
        errors and automatically deal with server health
        NOTE: For simplicity, uses a simple list request with an empty
        wildcard to check server health
        """
        try:
            func()
        except:
            print_error("Error: Something has gone wrong.")
            self.server_alive = False

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
            self.check_server_health()
            retry_multiplier = 1
            while True:
                if self.server_alive:
                    retry_multiplier = 1
                    raw_input = input("> Enter a command: ")
                    handler = self.parse_input(raw_input)
                    if handler:
                        self.safety_wrap(handler)
                else:
                    if retry_multiplier == 1:
                        print_error("It appears the server may be down, attempting to reconnect")
                    self.check_server_health()
                    if not self.server_alive:
                        print_error("Server is still down, trying again in {} seconds".format(retry_multiplier))
                        retry_multiplier *= 2
                        time.sleep(retry_multiplier)

if __name__ == '__main__':
    logging.basicConfig()
    instance = Client()
    instance.run()