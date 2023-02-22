# Testing

## Unit/Server Tests

For server tests we have written a suit of tests in the folder `server_tests` that utalize `pytest`. There are two files, `test_server.py` which tests our server implementation for part 1, and `test_grpc_server.py` which tests our server implementation for part 2. These tests are unit tests that focus on ensuring the server responds properly to the requests it receives. Furthermore, this behavior is verified with the integration tests implemented in the folder `client_tests`. 

### How to run

To run this test suite, ensure you have installed the requirements in `requirements.txt`  

Then switch into the `server_tests` folder 
```
cd unit_tests
```  
Then simply run the command:  
```
pytest
```

## Integration/Client Tests

In the part one folder (root) and part two folder you'll find a folder named `client_tests`. This contains automated tests that we wrote to test the integration of the client and the server.

### Setup

To run these tests, you will need to be on a computer capable of running bash scripts. Mac and Linux users, this should work for you out of the box. Windows users, you will likely have to install [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

You may also need to install the `pv` command. Doing this using homebrew is likely the easiest.

To test if you've installed everything correctly, try going into the `root/client_tests` and typing

```
./test01.sh
```

If this prints something (either success or failure) after about a second, you're all set. If this does not work, try these resources for help:

- [Mac](https://support.apple.com/guide/terminal/intro-to-shell-scripts-apd53500956-7c5b-496b-a362-2845f2aab4bc/mac)
- [Windows1](https://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/), [Windows2](https://www.geeksforgeeks.org/use-bash-shell-natively-windows-10/)

Still not working? To see what the tests are doing, you can open up `input/XYA_client.in` and see. Essentially, each one of these tests spins up a server in the background, and then runs a various number of clients in a particular order and ensures the output on the server and all the clients is what is expected. The shell scripts simply automate the process of running the server and client. You can go through manually one by one and run the server and client(s) and enter the commands identical to the .in files.

You may notice some `sleep X` commands in the `client.in`s. This is a bit of a developer hack, but this command essentially tells the client to wait. It's useful when doing stuff like having A send B a message, then simulating what would happen if the user did nothing for five seconds, which allows a message from B to appear. If you are unable to get the scripts working, you should be able to copy all of these tests manually. But we highly recommend putting in the effort to get the scripts running.

### Overview of the Tests

- 1: Basic connection
- 2: Multiple connections
- 3: Create
- 4: Login
- 5: List
- 6: Send immediately
- 7: Send on demand
- 8: Delete

### Running the Tests

To run a single test, simply run `./test0X.sh`. It may take ~10 seconds (or more). It should automatically print out success or failure, as well as the test description.

To run multiple tests, run `./run_tests.sh start stop`. This will run tests `start...stop` (inclusive) in sequence.

To run all the tests, run `./run_all.sh`.

## Is this testing scheme complete?

Taking a look at this testing scheme, you may have noticed that while we have more "traditional" unit tests that operate on specific instances of the server, by function, our client tests operate at the level of input output. Is this okay?

Yes. To see why, first notice that our server unit tests have complete coverage of both servers. Thus, if these server tests succeed, we can correctly assume that the server functions work correctly.

Then, think about what is necessary to test the client. Every client function interacts with the server. Thus, to fully test it, we must either completely mock the server (too much work), or trust our tests for server and treat it as a black box.

Then, notice that the tests we have here are functionally unit tests on the client server pair operating as unit. Each client spins up, does a very specific, smallest unit of action, and we must have the output matching what is expected exactly. Based on how we have defined these tests, there is complete coverage of the client code and the server code.

We also have the added benefit that testing this way also tests our marshaling / unmarshaling at the same time. It is the most accurate form of testing, because it asserts that all of the pieces run correctly in sequence and work together as intented. This, combined with the fact that our shell scripts focus on the smallest unit of work at a time and match output exactly, are sufficient to ensure proper functionality across all of the server and client.
