import unittest
from google.protobuf import message as _message
import sys

try:
    del sys.modules["server"]
except:
    pass
sys.path.insert(0, "..")
import server
import schema
import client
import threading
import grpc
import ctypes
from concurrent import futures

class Test_server(unittest.TestCase):
    """Test class for our part 2 server code"""

    def test_handle_create(self):

        # Create test server
        executor = futures.ThreadPoolExecutor()
        s = server.Server(host='127.0.0.1', port='50051', executor=executor)

        # Ensure server starts with no users
        assert len(s.users) == 0

        # Ensure user is added to user list when receiving create request object
        req = schema.Request(user_id="ream")
        s.handle_create(req)
        assert len(s.users) == 1

        # Ensure that error message is returned when user tries to create existing username and phantom user is not created
        out = s.handle_create(req)
        assert not out.success
        assert len(s.users) == 1
        
    
    def test_Login(self):
        
        # Create test server
        executor = futures.ThreadPoolExecutor()
        s = server.Server(host='127.0.0.1', port='50051', executor=executor)
        
        # Create test user
        req = schema.Request(user_id="ream")
        s.handle_create(req)

        # Ensure error when attempting to login to account that is already logged in
        ret = s.handle_login(req)
        assert not ret.success
        assert "already logged in" in ret.error_message

        # Log test user out
        s.users[req.user_id].is_logged_in = False

        # Test Login on user
        s.handle_login(req)
        assert s.users[req.user_id].is_logged_in == True

        # Test Login on nonexistant user
        bad_req = schema.Request(user_id="faker")
        ret = s.handle_login(bad_req)
        assert not ret.success
        assert "does not exist" in ret.error_message

    def test_List(self):

        # Create test server
        executor = futures.ThreadPoolExecutor()
        s = server.Server(host='127.0.0.1', port='50051', executor=executor)

        # Create test users
        names = ["ream", "mark", "achele", "joe", "bob"]
        for name in names:
            req = schema.Request(user_id=name)
            s.handle_create(req)

        # Ensure all match works
        empty_lst_req = schema.ListRequest(user_id='ream',wildcard="", page=0)
        ret = s.handle_list(empty_lst_req)
        assert len(ret.accounts) == 4

        # Ensure pagination works
        empty_lst_req = schema.ListRequest(user_id='ream',wildcard="", page=1)
        ret = s.handle_list(empty_lst_req)
        assert len(ret.accounts) == 1

        # Ensure filtering works
        e_lst_req = schema.ListRequest(user_id='ream', wildcard="e", page=0)
        ret = s.handle_list(e_lst_req)
        assert len(ret.accounts) == 3

        # Ensure none match works
        z_lst_req = schema.ListRequest(user_id='ream', wildcard="z", page=0)
        ret = s.handle_list(z_lst_req)
        assert len(ret.accounts) == 0

    def test_Delete(self):
        # Create test server
        executor = futures.ThreadPoolExecutor()
        s = server.Server(host='127.0.0.1', port='50051', executor=executor)

        # Create test users
        names = ["ream", "mark", "achele", "joe", "bob"]
        for name in names:
            req = schema.Request(user_id=name)
            s.handle_create(req)
        
        # Ensure no deletion if no such user exists
        req = schema.Request(user_id="jimmy")
        ret = s.handle_delete(req)
        assert not ret.success
        assert len(s.users) == 5

        # Ensure deletion for matching user works
        req = schema.Request(user_id="ream")
        ret = s.handle_delete(req)
        assert ret.success
        assert len(s.users) == 4
