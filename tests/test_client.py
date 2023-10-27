"""
Client class test suite
"""

import unittest

from client import Client


class TestClient(unittest.TestCase):
    """
    Test suite for Client class
    """

    def test_parse_host_name_localhost(self) -> None:
        """Test parsing localhost as hostname"""
        Client.parse_hostname("localhost")

    def test_parse_host_name_ip_address(self) -> None:
        """Test parsing an IP address as hostname"""
        Client.parse_hostname("1.1.1.1")

    def test_parse_host_name_domain_name(self) -> None:
        """Test parsing a domain name as hostname"""
        Client.parse_hostname("www.duckduckgo.com")

    def test_parse_host_name_invalid(self) -> None:
        """Test parsing an invalid hostname"""
        self.assertRaises(ValueError, Client.parse_hostname, "invalid")

    def test_parse_username_valid(self) -> None:
        """Test parsing a valid username"""
        Client.parse_username("John")

    def test_parse_username_empty(self) -> None:
        """Test that parsing an empty username raises a ValueError"""
        self.assertRaises(ValueError, Client.parse_username, "")

    def test_parse_username_too_long(self) -> None:
        """Test that parsing a username that is too long raises a ValueError"""
        self.assertRaises(ValueError, Client.parse_username, "a" * 256)
