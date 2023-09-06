#ifndef __CLIENT_H__
#define __CLIENT_H__

#include "message.h"
#include <string>

class Client
{
public:
    Client(const std::string &host, const uint16_t port, const std::string &sender);
    ~Client();

    void connect_to_server();

    void send_message(Message &message);
    Message receive_message();

    int get_fd()
    {
        return m_fd;
    }

private:
    const uint16_t m_port;
    const std::string m_host;
    const std::string m_sender;
    int m_fd;
};

#endif // __CLIENT_H__
