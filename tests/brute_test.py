"""
This file is used to test the server with a large number of requests.
It is not a unit test, but rather a script that executes a large number of
client requests to test the server's ability to correctly set the `more_messages` flag.
"""

import subprocess as sp

with open("tests/resources/names.txt", encoding="utf8") as names_file:
    names = names_file.readlines()

for name in names:
    client_program = ["python3", "client.py", "localhost", "1024", name, "create"]

    with sp.Popen(client_program, text=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE) \
            as process:
        try:
            output, errors = process.communicate(input="John\nHello")
        except sp.TimeoutExpired:
            output, errors = process.communicate()
        print(output)
        print(errors)

with sp.Popen(["python3", "client.py", "localhost", "1024", "John", "read"],
              text=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE) as process:
    output, errors = process.communicate()

print(output)
print(errors)
