import subprocess as sp

with open('resources/names.txt') as names_file:
    names = names_file.readlines()

for name in names:
    client_program = ["python3", "client.py", "localhost", "1024", name, "create"]

    process = sp.Popen(client_program, text=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    try:
        output, errors = process.communicate(input="John\nHello")
    except sp.TimeoutExpired:
        process.kill()
        output, errors = process.communicate()
    print(output)
    print(errors)

    process.terminate()

read = sp.Popen(["python3", "client.py", "localhost", "1024", "John", "read"],
                text=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
output, errors = read.communicate()

print(output)
print(errors)
