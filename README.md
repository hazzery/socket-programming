# Socket Programming
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

# Usage Instructions

To start the server program, execute the following command in the project directory.
```bash
python3 server.py <port_number>
```
This starts up a welcoming socket, which listens for client connections
on the specified `port_number` for incoming connections.


To send and read messages, you must execute the client program using the following command.
```bash
python3 client.py <server_address> <port_number> <username> <message_type>
```
Here, `server_address` is the IP address of the computer in which the server program is running on,
`port_number` is the port number on which the server program is listening for incoming connections,
`username` is the name of the client connecting to the server, and `message_type` is the type of
request to send to the server. This can be either `create` to send somebody a message,
or `read` to receive messages that have been sent to you.

Upon making a Create request, you will be prompted to enter the name of the
recipient of your message, and the message you would like to send them.

## Example Usage
### Server
```bash
python3 server.py 12000
```

### Client 1
```bash
python3 client.py localhost 12000 Alice create
John
Hello John! How are you?
```

### Client 2
```bash
python3 client.py localhost 12000 John read
```
