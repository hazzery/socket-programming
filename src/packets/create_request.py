"""Home to the ``CreateReqeust`` class."""

import logging
import struct

from src.packets.packet import Packet

logger = logging.getLogger(__name__)


class CreateRequest(Packet, struct_format="!BH"):
    """Encoding and decoding of create request packets.

    Usage:
        create_request = CreateRequest("sender name", "receiver name", "Hi")
        packet = create_request.to_bytes()

        sender_name, receiver_name, message = CreateRequest.decode_packet(record)
    """

    def __init__(
        self,
        receiver_name: str,
        encrypted_message: bytes,
    ) -> None:
        """Encode a create request packet.

        :param user_name: The name of the user sending the request.
        :param receiver_name: The name of the message recipient.
        :param message: The string message to be sent.
        """
        self.receiver_name = receiver_name
        self.encrypted_message = encrypted_message

    def to_bytes(self) -> bytes:
        """Return the create request packet.

        :return: A byte array holding the create request.
        """
        logger.debug(
            "Create create request addressed to %s",
            self.receiver_name,
        )

        packet = struct.pack(
            self.struct_format,
            len(self.receiver_name.encode()),
            len(self.encrypted_message),
        )

        packet += self.receiver_name.encode()
        packet += self.encrypted_message

        return packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[str, bytes]:
        """Decode a message request packet.

        :param packet: An array of bytes containing the create request.
        :raises ValueError: If the packet has incorrect values.
        :return: A tuple containing the name of the message recipient
        and the message itself.
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

        encrypted_message = payload[index : index + message_size]

        return receiver_name, encrypted_message
