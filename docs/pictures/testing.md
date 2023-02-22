# Testing

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

### Running the Tests

To run a single test, simply run `./test0X.sh`. It may take ~10 seconds (or more). It should automatically print out success or failure, as well as the test description.

To run multiple tests, run `./run_tests.sh start stop`. This will run tests `start...stop` (inclusive) in sequence.

To run all the tests, run `./run_all.sh`.
