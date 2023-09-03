#include "client.h"

int main()
{
    Client client("192.168.1.100", 8080);

    client.connect_to_server();
    client.send_message("Hello, Server!");

    return 0;
}