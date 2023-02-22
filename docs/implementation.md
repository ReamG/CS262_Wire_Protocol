# Implementation

The specs as given define a certain set of functions that must be possible within our chat application, but they are not comprehensive enough to define what we might call an "app". This document lays out our specific implementation/interpretation of the spec. It contains information about everything that is possible in our system as well as justification for decisions we made.

## High Level Overview

Our chat app is based around `user`s. The only data stored about each `user` (in the server's memory, not persistent) is their username. **There are no passwords or any other metadata about users besides their username**. Each username must be unique, but uppercase, lowercase, and special characters are allowed.

The chat app does stuff by sending messages. All messages are capped at 280 characters. Messagees cannot contain newlines.

Each client session can sign into at most one user. That means if you want to "log out", you must kill the client and run it again, this time logging in with a different user.

When users are logged in, any messages sent to them are immediately delivered and printed above their current line in the terminal. When users are logged out, the messages are sent to a queue, and delivered immediately the next time they log in. **NOTE: In our implementation this fulfils both specs 3 and 4.** You can think of it as the server constantly "delivering undelivered messages" and the client "constantly demading them". Both of these notions are fulfilled by this design, and we felt it was by far the most natural way to design a chat app that must meet this specs.

## User Interface (a.k.a available commands)
