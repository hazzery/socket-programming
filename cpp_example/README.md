# CPP Version

## Setup

First setup a dummy ip address, I am using `192.168.1.100`:
```
ip link add dummy0 type dummy
ip addr add 192.168.1.100/24 dev dummy0
ip link set dummy0 up
```

To confirm its setup properly:
```
ip addr show dummy0

6: dummy0: <BROADCAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
    ...
    inet 192.168.1.100/24 scope global dummy0
       valid_lft forever preferred_lft forever
    ...

```

## Build

From the project directory:
```
mkdir cpp_example/build
cd ./cpp_example/build
cmake ..
make 
```

## Run

Start atleast 3 terminals, one for the server and 2 for clients

### Server

From the build directory:
```
./Server
```

### Client
```
./Client <client name>

./Client Alice
./Client John
```

Once in a client begin typing a message to another client by typing:
```
<receiver name>,<message>

Alice,Hello # From John's terminal
John,What is up? # From Alice's terminal
``` 


