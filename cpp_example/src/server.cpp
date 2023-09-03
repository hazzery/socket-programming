#include "server.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <iostream>

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

void Server::run_server()
{
    int client_fd = accept(m_fd, nullptr, nullptr);

    if (client_fd == -1)
    {
        return;
    }

    uint8_t *read_buffer = new uint8_t[4096];

    while (true)
    {

        // Read from the client socket
        int ret = read(client_fd, read_buffer, 4096);

        // -1 => error, 0 => EOF
        if (ret == -1 || ret == 0)
        {
            break;
        }

        std::cout << (int)read_buffer << std::endl;
    }

    delete[] read_buffer;

    // Close the connection
    close(client_fd);
}
