#include "server.h"
#include "message.h"

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>

#include <iostream>
#include <vector>

Server::Server(const std::string &host, const uint16_t port) : m_host(host), m_port(port)
{
    std::cout << "Starting server at: " << m_host << ":" << m_port << std::endl;

    // Create the welcoming socket
    if ((m_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        return;
    }

    // Initialize the server_address
    sockaddr_in server_address;
    memset(&server_address, 0, sizeof(server_address));
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(m_port);
    server_address.sin_addr.s_addr = inet_addr(m_host.c_str());

    // Bind the socket
    if (bind(m_fd, (sockaddr *)&server_address, sizeof(server_address)) < 0)
    {
        std::cerr << "Error binding the socket to the given port." << std::endl;

        return;
    }

    // Listen for connections
    if (listen(m_fd, 5) < 0)
    {
        std::cerr << "Error while trying to listen on the port." << std::endl;

        return;
    }

    // Server main loop
    m_server_thread = std::thread(&Server::run_server, this);
}

Server::~Server()
{
    std::cout << "Stopping server at: " << m_host << ":" << m_port << std::endl;
    close(m_fd);
}

void Server::handle_client(int client_fd)
{
    uint8_t *read_buffer = new uint8_t[4096];
    int read_len = 0;

    std::string client_name;

    while (true)
    {
        read_len = read(client_fd, read_buffer, 4096);

        if (read_len == -1 || read_len == 0)
        {
            break;
        }

        Message message = Message::decode(read_buffer, read_len);
        client_name = message.sender;
        client_map[client_name] = client_fd;

        if (message.type == Type::CREATE)
        {
            std::cout << "Added client: " << client_name << std::endl;
            continue;
        }

        // Forward the message to the intended receiver
        if (client_map.count(message.receiver) != 0)
        {
            int receiver_fd = client_map[message.receiver];
            write(receiver_fd, read_buffer, read_len);
        }
    }

    delete[] read_buffer;
    client_map.erase(client_name); // remove the client from the map

    std::cout << "Removed client: " << client_name << std::endl;

    close(client_fd);
}

void Server::run_server()
{
    std::vector<std::thread> client_threads;

    while (true)
    {
        int client_fd = accept(m_fd, nullptr, nullptr);

        if (client_fd == -1)
        {
            continue;
        }

        std::thread client_thread(&Server::handle_client, this, client_fd);
        // Detach the thread, allowing it to clean up itself when done - no need to rejoin
        client_thread.detach();
    }
}
