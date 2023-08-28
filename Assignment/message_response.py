from pythonlangutil.overload import Overload, signature
from .message_type import MessageType
from .record import Record


class MessageResponse(Record):

    @Overload
    @signature("str", "dict")
    def __init__(self, receiver_name: str, messages: dict[str, list[tuple[str, bytes]]]):
        """
        Encodes a record containing all (up to 255) messages for the specified sender
        :param messages:
        :param receiver_name: The string name of the client requesting their messages
        """
        num_messages = len(messages.get(receiver_name, []))
        more_messages = False
        if num_messages > 255:
            more_messages = True
            num_messages = 255

        self.record = bytearray(5)

        self.record[0] = Record.MAGIC_NUMBER >> 8
        self.record[1] = Record.MAGIC_NUMBER & 0xFF
        self.record[2] = MessageType.RESPONSE.value
        self.record[3] = num_messages
        self.record[4] = int(more_messages)

        for i in range(num_messages):
            sender, message = messages[receiver_name][i]

            self.record.append(len(sender.encode()))
            self.record.append(len(message) >> 8)
            self.record.append(len(message) & 0xFF)
            self.record.extend(sender.encode())
            self.record.extend(message)

            print(f"{sender}'s message: \"{message.decode()}\" "
                  f"has been delivered to {receiver_name}")

        del messages.get(receiver_name, [])[:num_messages]

    @__init__.overload
    @signature("bytes")
    def __init__(self, record: bytes):
        """
        Decodes a message response packet
        :param record: The packet to be decoded
        """
        magic_number = record[0] << 8 | record[1]
        if magic_number != Record.MAGIC_NUMBER:
            raise ValueError("Invalid magic number when decoding message response")

        try:
            message_type = MessageType(record[2])
        except ValueError:
            raise ValueError("Invalid message type when decoding message response")
        if message_type != MessageType.RESPONSE:
            raise ValueError(f"Message type {message_type} found when decoding message response, "
                             f"expected RESPONSE")

        num_messages = record[3]
        self.more_messages = bool(record[4])
        self.messages: list = [None] * num_messages

        index = 0
        for _ in range(num_messages):
            sender_name_length = record[index]
            index += 1

            message_length = (record[index] << 8) | (record[index + 1] & 0xFF)
            index += 2

            sender_name = record[index:index + sender_name_length].decode()
            index += sender_name_length

            message = record[index:index + message_length].decode()
            index += message_length

            self.messages.append((sender_name, message))
