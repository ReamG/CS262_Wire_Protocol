import pytest
import unittest
from google.protobuf import message as _message
import sys

sys.path.insert(0, "../part2")
import client
import server
import threading
import grpc
import schema_pb2 as schema
import schema_pb2_grpc as services
import ctypes
from concurrent import futures

class Test_GRPC_Server(unittest.TestCase):
    """Test class for our part 2 server code"""

    def test_Create(self):

        # Create test server
        executor = futures.ThreadPoolExecutor()
        s = server.ChatHandlerServicer(executor)

        # Ensure server starts with no users
        assert len(s.users) == 0

        # Ensure user is added to user list when receiving create request object
        req = schema.Credentials(user_id="ream")
        s.Create(req, None)
        assert len(s.users) == 1

        # Ensure that error message is returned when user tries to create existing username and phantom user is not created
        out = s.Create(req, None)
        assert not out.success
        assert len(s.users) == 1
    
    def test_Login(self):
        
        # Create test server
        executor = futures.ThreadPoolExecutor()
        s = server.ChatHandlerServicer(executor)
        
        # Create test user
        req = schema.Credentials(user_id="ream")
        s.Create(req, None)

        # Ensure error when attempting to login to account that is already logged in
        ret = s.Login(req, None)
        assert not ret.success
        assert "already logged in" in ret.error_message

        # Log test user out
        s.users[req.user_id].is_logged_in = False

        # Test Login on user
        s.Login(req, None)
        assert s.users[req.user_id].is_logged_in == True

        # Test Login on nonexistant user
        bad_req = schema.Credentials(user_id="faker")
        ret = s.Login(bad_req, None)
        assert not ret.success
        assert "does not exist" in ret.error_message

    def test_List(self):

        # Create test server
        executor = futures.ThreadPoolExecutor()
        s = server.ChatHandlerServicer(executor)

        # Create test users
        names = ["ream", "mark", "achele", "joe", "bob"]
        for name in names:
            req = schema.Credentials(user_id=name)
            s.Create(req, None)

        # Ensure all match works
        empty_lst_req = schema.ListRequest(wildcard="")
        ret = s.List(empty_lst_req, None)
        assert len(ret.accounts) == 5

        # Ensure filtering works
        e_lst_req = schema.ListRequest(wildcard="e")
        ret = s.List(e_lst_req, None)
        assert len(ret.accounts) == 3

        # Ensure none match works
        z_lst_req = schema.ListRequest(wildcard="z")
        ret = s.List(z_lst_req, None)
        assert len(ret.accounts) == 0

    def test_Delete(self):
        # Create test server
        executor = futures.ThreadPoolExecutor()
        s = server.ChatHandlerServicer(executor)

        # Create test users
        names = ["ream", "mark", "achele", "joe", "bob"]
        for name in names:
            req = schema.Credentials(user_id=name)
            s.Create(req, None)
        
        # Ensure no deletion if no such user exists
        req = schema.Credentials(user_id="jimmy")
        ret = s.Delete(req, None)
        assert not ret.success

        # Ensure deletion for matching user works
        req = schema.Credentials(user_id="ream")
        ret = s.Delete(req, None)
        assert ret.success
        assert len(s.users) == 4