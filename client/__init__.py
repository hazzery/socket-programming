"""
Client package
==================

The client package is directly executable using::

    python3 -m client <hostname> <port_number> <username> <message_type>

"""

from .client import Client

__all__ = ["Client"]
