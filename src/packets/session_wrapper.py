"""Home to the ``SessionWrapper`` class."""

import struct

from src.packets.packet import Packet


class SessionWrapper(Packet, struct_format="!?"):
    """Wrapper class to prepend the client session token to packets."""

    SESSION_TOKEN_LENGTH = 32

    def __init__(self, session_token: bytes | None, payload: Packet) -> None:
        """Initialise the packet.

        :param session_token: The client's current session token.
        """
        if (
            session_token is not None
            and len(session_token) != SessionWrapper.SESSION_TOKEN_LENGTH
        ):
            raise ValueError("Session token is incorrect length")

        self.session_token = session_token
        self.payload = payload

    def to_bytes(self) -> bytes:
        """Convert the packet into a ``bytes`` object.

        :return: A ``bytes`` object encoding the packet and it's session.
        """
        packet = struct.pack(
            SessionWrapper.struct_format,
            self.session_token is not None,
        )

        if self.session_token is not None:
            packet += self.session_token

        packet += self.payload.to_bytes()

        return packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[bytes | None, bytes]:
        """Decode the packet into its token and payload.

        :param packet: The packet to decode.
        :return: A tuple of the session token and payload.
        """
        header_fields: tuple[bool]
        header_fields, payload = cls.split_packet(packet)
        (has_token,) = header_fields

        session_token = None

        if has_token:
            session_token, payload = (
                payload[: SessionWrapper.SESSION_TOKEN_LENGTH],
                payload[SessionWrapper.SESSION_TOKEN_LENGTH :],
            )

        return session_token, payload
