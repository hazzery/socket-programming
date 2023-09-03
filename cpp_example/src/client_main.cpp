#include "client.h"

#include <poll.h>
#include <unistd.h>

#include <thread>
#include <iostream>

void poll_thread(Client &client)
{
    pollfd fds[2];
    fds[0].fd = STDIN_FILENO;
    fds[0].events = POLLIN;

    fds[1].fd = client.get_fd();
    fds[1].events = POLLIN;

    std::string input_str;

    while (true)
    {
        int ret = poll(fds, 2, -1);

        if (ret > 0)
        {
            if (fds[0].revents & POLLIN)
            {
                std::getline(std::cin, input_str);

                std::istringstream iss(input_str);
                std::vector<std::string> components;

                std::string token;
                while (std::getline(iss, token, ','))
                {
                    components.push_back(token);
                }

                if (components.size() < 2)
                {
                    std::cout << "Incomplete message. Please provide all components [Receiver,Message]" << std::endl;
                    continue;
                }

                Message message;
                message.type = Type::RESPONSE;
                message.receiver = components[0];
                message.contents = components[1];

                client.send_message(message);
            }

            if (fds[1].revents & POLLIN)
            {
                Message received_msg = client.receive_message();
                std::cout << "Received message: " << received_msg.to_string() << std::endl;
            }
        }
    }
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        std::cerr << "Usage: " << argv[0] << " <sender_name>" << std::endl;
        return 1;
    }

    std::string sender_name = argv[1];

    Client client("192.168.1.100", 8080, sender_name);
    client.connect_to_server();

    // Register client
    Message message;
    message.type = Type::CREATE;
    client.send_message(message);

    std::thread poll_thr(poll_thread, std::ref(client));

    while (true)
    {
        std::this_thread::sleep_for(std::chrono::seconds::max());
    }

    poll_thr.join();

    return 0;
}