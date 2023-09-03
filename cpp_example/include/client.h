#ifndef __CLIENT_H__
#define __CLIENT_H__

#include <string>

class Client
{
public:
    Client(const std::string &host, const uint16_t port);
    ~Client();

    void connect_to_server();
    void send_message(const std::string &message);

private:
    const uint16_t m_port;
    const std::string m_host;
    int m_fd;
};

#endif // __CLIENT_H__
