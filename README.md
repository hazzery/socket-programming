# Socket Programming

![unittests passing](https://github.com/hazzery/socket-programming/actions/workflows/unittests.yml/badge.svg)
[![codecov](https://codecov.io/gh/hazzery/socket-programming/graph/badge.svg?token=6GQA3I43XT)](https://codecov.io/gh/hazzery/socket-programming)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/hazzery/socket-programming/master.svg)](https://results.pre-commit.ci/latest/github/hazzery/socket-programming/master)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

## Usage Instructions

To run both the server and client, the project dependencies must be installed.
Create a virtual environment inside the project directory and run `pip install`.

```bash
python3 -m venv venv
source venv/bin/activate
pip install .
```

We must also create a certificate so that the client can verify it is
communicating with the correct server (using SSL). Currently the certificate
must be called `server_cert.pem` and the private key must be called
`server_key.pem`. You can create these by running `openssl`.

```bash
openssl req -x509 -newkey rsa:2048 -keyout server_key.pem -out server_cert.pem -days 365
```

To start the server program, execute the following command in the project directory.

```bash
python3 -m server <port_number>
```

This starts up a welcoming socket, which listens for client connections
on the specified `port_number` for incoming connections.

To send and read messages, you must execute the client program using the
following command.

```bash
python3 -m client <server_address> <port_number> <username>
```

Here, `server_address` is the IP address of the computer in which the server
program is running on, `port_number` is the port number on which the server
program is listening for incoming connections, `username` is the name of the
client connecting to the server.

Running the client will prompt you to input the name of the request you wish to
perform.

- `register` sends your name and randomly generated RSA public key to the server
- `login` has the server generate you a session token used to validate requests
- `key` requests another user's public key so you can send them messages
- `create` to send somebody a message
- `read` to receive messages that have been sent to you.

Note: All request names are case-insensitive, so can be capitalised if you like

Upon making a create, you will be prompted to enter the name of the recipient
of your message, and the message you would like to send them. Making a key
request will prompt you to enter the name of the user whose key you want.

## Example Usage

### Server

```bash
python3 -m server 12000
```

### Client 1

```bash
python3 -m client localhost 12000 Alice
create
John
Hello John! How are you?
```

### Client 2

```bash
python3 -m client localhost 12000 John
read
```

## Licence

This project is licenced under the GNU AGPL version 3

![AGPLv3](https://www.gnu.org/graphics/agplv3-with-text-162x68.png)
