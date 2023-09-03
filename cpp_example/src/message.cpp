#include "message.h"
#include <stdexcept>

std::string type_to_str(Type type)
{
    switch (type)
    {
    case Type::READ:
        return "READ";
    case Type::CREATE:
        return "CREATE";
    case Type::RESPONSE:
        return "RESPONSE";
    }

    return "";
}

std::vector<uint8_t> Message::encode(const Message &message)
{
    std::vector<uint8_t> bytes;
    bytes.resize(7);

    bytes[0] = static_cast<uint8_t>(MAGIC_NUMBER >> 8);
    bytes[1] = static_cast<uint8_t>(MAGIC_NUMBER & 0xFF);

    bytes[2] = static_cast<uint8_t>(message.type);

    bytes[3] = static_cast<uint8_t>(message.sender.size());
    bytes[4] = static_cast<uint8_t>(message.receiver.size());
    uint16_t msg_length = static_cast<uint16_t>(message.contents.size());
    bytes[5] = static_cast<uint8_t>(msg_length >> 8);
    bytes[6] = static_cast<uint8_t>(msg_length & 0xFF);

    for (auto ch : message.sender)
    {
        bytes.push_back(static_cast<uint8_t>(ch));
    }

    for (auto ch : message.receiver)
    {
        bytes.push_back(static_cast<uint8_t>(ch));
    }

    for (auto ch : message.contents)
    {
        bytes.push_back(static_cast<uint8_t>(ch));
    }

    return bytes;
}

Message Message::decode(const uint8_t *message_bytes, size_t len)
{
    if (message_bytes == nullptr || len < 7)
    {
        throw std::runtime_error("Invalid input.");
    }

    uint16_t magic_number = static_cast<uint16_t>((message_bytes[0] << 8) | message_bytes[1]);
    if (magic_number != MAGIC_NUMBER)
    {
        throw std::runtime_error("Incorrect magic number.");
    }

    Type type = static_cast<Type>(message_bytes[2]);
    size_t sender_length = message_bytes[3];
    size_t receiver_length = message_bytes[4];
    size_t message_length = (message_bytes[5] << 8) | message_bytes[6];

    if (len < 7 + sender_length + receiver_length + message_length)
    {
        throw std::runtime_error("Incomplete message.");
    }

    size_t index = 7;
    std::string sender(reinterpret_cast<const char *>(message_bytes + index), sender_length);
    index += sender_length;

    std::string receiver(reinterpret_cast<const char *>(message_bytes + index), receiver_length);
    index += receiver_length;

    std::string message(reinterpret_cast<const char *>(message_bytes + index), message_length);

    return {type, sender, receiver, message};
}
