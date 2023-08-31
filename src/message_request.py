from pythonlangutil.overload import Overload, signature
from message_type import MessageType
from record import Record


class MessageRequest(Record):

    @Overload
    @signature("MessageType", "str", "str", "str")
    def __init__(self, message_type: MessageType, user_name: str,
                 receiver_name: str, message: str):
        """
        Encodes a message request packet
        :param message_type: The type of the request (READ or CREATE)
        :param user_name: The name of the user sending the request
        :param receiver_name: The name of the message recipient
        :param message: The message to be sent
        """

        self.record = bytearray(7)
        self.record[0] = Record.MAGIC_NUMBER >> 8
        self.record[1] = Record.MAGIC_NUMBER & 0xFF
        self.record[2] = message_type.value
        self.record[3] = len(user_name.encode())
        self.record[4] = len(receiver_name.encode())
        self.record[5] = len(message.encode()) >> 8
        self.record[6] = len(message.encode()) & 0xFF

        self.record.extend(user_name.encode())
        self.record.extend(receiver_name.encode())
        self.record.extend(message.encode())

    def to_bytes(self) -> bytes:
        """
        Returns the message request packet
        :return: A byte array holding the message request
        """
        return bytes(self.record)

    @__init__.overload
    @signature("bytes")
    def __init__(self, record: bytes):
        """
        Decodes a message request packet
        :param record: An array of bytes containing the message request
        """
        magic_number = record[0] << 8 | record[1]
        if magic_number != Record.MAGIC_NUMBER:
            raise ValueError("Received message request with incorrect magic number")

        if 1 <= record[2] <= 2:
            self.message_type = MessageType(record[2])
        else:
            raise ValueError("Received message request with invalid ID")

        user_name_length = record[3]
        receiver_name_length = record[4]
        message_length = record[5] << 8 | record[6]

        if user_name_length < 1:
            raise ValueError("Received message request with insufficient user name length")

        if self.message_type == MessageType.READ:
            if receiver_name_length != 0:
                raise ValueError("Received read request with non-zero receiver name length")
            if message_length != 0:
                raise ValueError("Received read request with non-zero message length")

        elif self.message_type == MessageType.CREATE:
            if receiver_name_length < 1:
                raise ValueError("Received create request with insufficient receiver name length")
            if message_length < 1:
                raise ValueError("Received create request with insufficient message length")

        index = 7

        self.user_name = record[index:index + user_name_length].decode()
        index += user_name_length

        self.receiver_name = record[index:index + receiver_name_length].decode()
        index += receiver_name_length

        self.message = record[index:index + message_length]

    def decode(self) -> tuple[MessageType, str, str, bytes]:
        """
        Decodes the message request packet
        :return: A tuple containing the message type, username, receiver name and message
        """
        return self.message_type, self.user_name, self.receiver_name, self.message
