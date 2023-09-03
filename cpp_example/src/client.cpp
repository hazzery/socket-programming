#include "client.h"
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <iostream>
#include <cstring>

Client::Client(const std::string &host, const uint16_t port) : m_host(host), m_port(port)
{
    std::cout << "Starting client at: " << m_host << ":" << m_port << std::endl;
}

Client::~Client()
{
    std::cout << "Stopping client at: " << m_host << ":" << m_port << std::endl;
    close(m_fd);
}

void Client::connect_to_server()
{
    if ((m_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        std::cout << "Socket creation error" << std::endl;
        return;
    }

    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(m_port);

    if (inet_pton(AF_INET, m_host.c_str(), &server_address.sin_addr) <= 0)
    {
        std::cout << "Invalid address / Address not supported" << std::endl;
        return;
    }

    if (connect(m_fd, (sockaddr *)&server_address, sizeof(server_address)) < 0)
    {
        std::cout << "Connection failed" << std::endl;
        return;
    }

    std::cout << "Connected to the server" << std::endl;
}

void Client::send_message(const std::string &message)
{
    send(m_fd, message.c_str(), message.size(), 0);
    std::cout << "Message sent" << std::endl;
}
