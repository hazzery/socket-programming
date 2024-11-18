"""Client class test suite."""

import unittest

from src.parse_hostname import parse_hostname
from src.parse_username import parse_username


class TestClientParseArguments(unittest.TestCase):
    """Test suite for Client class."""

    def test_parse_host_name_localhost(self) -> None:
        """Test parsing localhost as hostname."""
        parse_hostname("localhost")

    def test_parse_host_name_ip_address(self) -> None:
        """Test parsing a valid IP address as hostname."""
        parse_hostname("1.1.1.1")

    def test_parse_host_name_domain_name(self) -> None:
        """Test parsing a domain name as hostname."""
        parse_hostname("www.duckduckgo.com")

    def test_parse_host_name_invalid(self) -> None:
        """Test parsing an invalid hostname."""
        self.assertRaises(ValueError, parse_hostname, "invalid")

    def test_parse_host_name_invalid_ip(self) -> None:
        """Test parsing an invalid IP address as hostname."""
        self.assertRaises(ValueError, parse_hostname, "256.0.0.1")

    def test_parse_username_min_length(self) -> None:
        """Test parsing a valid username with minimum length."""
        parse_username("J")

    def test_parse_username_max_length(self) -> None:
        """Test parsing a valid username with maximum length."""
        parse_username("J" * 255)

    def test_parse_username_empty(self) -> None:
        """Test that parsing an empty username raises a ValueError."""
        self.assertRaises(ValueError, parse_username, "")

    def test_parse_username_too_long(self) -> None:
        """Test that parsing a username that is too long raises a ValueError."""
        self.assertRaises(ValueError, parse_username, "a" * 256)
