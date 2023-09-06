#include "client.h"

#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>

#include <iostream>
#include <cstring>

Client::Client(const std::string &host, const uint16_t port, const std::string &sender) : m_host(host), m_port(port), m_sender(sender)
{
    std::cout << "Starting client at: " << m_host << ":" << m_port << " with sender name: " << m_sender << std::endl;
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

    int flags = fcntl(m_fd, F_GETFL, 0);
    fcntl(m_fd, F_SETFL, flags | O_NONBLOCK);

    std::cout << "Connected to the server" << std::endl;
}

void Client::send_message(Message &message)
{
    message.sender = m_sender;
    std::vector<uint8_t> encoded_message = Message::encode(message);
    send(m_fd, encoded_message.data(), encoded_message.size(), 0);
}

Message Client::receive_message()
{
    uint8_t *buffer = new uint8_t[4096];
    int read_len;

    while (true)
    {
        read_len = read(m_fd, buffer, 4096);

        if (read_len <= 0)
        {
            continue;
        }

        return Message::decode(buffer, read_len);
    }
}