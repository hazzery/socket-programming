"""
Client side program for COSC264 socket programming assignment

Harrison Parkes (hpa101) 94852440
"""
import socket
import sys

from common import *

usage_prompt = "Usage: python3 client.py <host_name> <port_number> <user_name> <message_type>"

if len(sys.argv) != 5:
    print(usage_prompt)
    sys.exit(1)

if not sys.argv[2].isdigit():
    print(usage_prompt)
    print("Port number must be an integer")
    sys.exit(1)

port_number = int(sys.argv[2])

if not 1024 <= port_number <= 64000:
    print(usage_prompt)
    print("Port number must be between 1024 and 64000 (inclusive)")
    sys.exit(1)

host_name = sys.argv[1]

try:
    socket.getaddrinfo(host_name, port_number)
except socket.gaierror:
    print(usage_prompt)
    print("Invalid host name")
    sys.exit(1)

user_name = sys.argv[3]
if len(user_name.encode()) > 255:
    print(usage_prompt)
    print("Username must be at most 255 bytes")
    sys.exit(1)

try:
    message_type = MessageType[sys.argv[4].upper()]
except KeyError:
    print(usage_prompt)
    print("Invalid message type, must be \"read\" or \"create\"")
    sys.exit(1)

if message_type == MessageType.RESPONSE:
    print(usage_prompt)
    print("Message type \"response\" not allowed, must be \"read\" or \"create\"")
    sys.exit(1)

