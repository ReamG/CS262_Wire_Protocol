# Implementation

The specs as given define a certain set of functions that must be possible within our chat application, but they are not comprehensive enough to define what we might call an "app". This document lays out our specific implementation/interpretation of the spec. It contains information about everything that is possible in our system as well as justification for decisions we made.

## High Level Overview

Our chat app is based around `user`s. The only data stored about each `user` (in the server's memory, not persistent) is their username. **There are no passwords or any other metadata about users besides their username**. Each username must be unique, but uppercase, lowercase, and special characters are allowed.

The chat app does stuff by sending messages. All messages are capped at 280 characters. Messagees cannot contain newlines.

Each client session can sign into at most one user. That means if you want to "log out", you must kill the client and run it again, this time logging in with a different user.

When users are logged in, any messages sent to them are printed in the terminal. When users are logged out, the messages are sent to a queue, and delivered immediately the next time they log in. **NOTE: In our implementation this fulfils both specs 3 and 4.** You can think of it as the server constantly "delivering undelivered messages" and the client "constantly demading them". Both of these notions are fulfilled by this design, and we felt it was by far the most natural way to design a chat app that must meet this specs.

For deletes, we only allow authenticated users to delete their own account. Thus to delete an account you first log in as that user, then send a delete request.

## User Interface (a.k.a available commands)

`create` - Will prompt you for a username. Validates it and then attempts to create an account with that username. Automatically logs you in as this user you create if successful.

`login` - Will prompt you for a username. Logs you into this account if it exists, if not gives you an error. **NOTE: You must be logged in to run this command**.

`list` - First prompts you for a text wildcard, then prompts you for a page. To avoid ever having to send variable length stuff over the wire, we say that the list command will only return 4 accounts at a time. You can still successfully see all the users by paginating (i.e. issuing consecutive requests with the page number increasing). **NOTE: We start counting pages at _zero_, not one**.

`send` - Will prompt you for a recipient username then the message. Will make sure the mesage is the right length and send. As discussed above, if they are logged in this sens immediately, if they are not it is put in a queue and delivered on demand immediately the next time they log in.

`delete` - You must be logged in to run this command. Deletes your account and logs you out. If there were any messages in your account which hadn't been delivered, they are wiped and never to be seen.
