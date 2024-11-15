"""Home to the ``CreateReqeust`` class."""

import logging
import struct

from src.message_type import MessageType

from .packet import Packet

logger = logging.getLogger(__name__)


class CreateRequest(Packet, struct_format="!BH", message_type=MessageType.CREATE):
    """Encoding and decoding of create request packets.

    Usage:
        create_request = CreateRequest("sender name", "receiver name", "Hi")
        packet = create_request.to_bytes()

        sender_name, receiver_name, message = CreateRequest.decode_packet(record)
    """

    def __init__(
        self,
        session_token: bytes,
        receiver_name: str,
        message: str,
    ) -> None:
        """Encode a create request packet.

        :param user_name: The name of the user sending the request.
        :param receiver_name: The name of the message recipient.
        :param message: The string message to be sent.
        """
        super().__init__(session_token=session_token)
        self.receiver_name = receiver_name
        self.message = message
        self.packet = b""

    def to_bytes(self) -> bytes:
        """Return the create request packet.

        :return: A byte array holding the create request.
        """
        logger.debug(
            'Creating create request to send %s the message "%s"',
            self.receiver_name,
            self.message,
        )

        self.packet = super().to_bytes()

        self.packet += struct.pack(
            self.struct_format,
            len(self.receiver_name.encode()),
            len(self.message.encode()),
        )

        self.packet += self.receiver_name.encode()
        self.packet += self.message.encode()

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[str, bytes]:
        """Decode a message request packet.

        :param packet: An array of bytes containing the create request
        """
        header_fields, payload = cls.split_packet(packet)
        (
            receiver_name_size,
            message_size,
        ) = header_fields

        if receiver_name_size < 1:
            raise ValueError(
                "Received create request with insufficient receiver name length",
            )
        if message_size < 1:
            raise ValueError(
                "Received create request with insufficient message length",
            )

        receiver_name = payload[:receiver_name_size].decode()
        index = receiver_name_size

        message = payload[index : index + message_size]

        return receiver_name, message
