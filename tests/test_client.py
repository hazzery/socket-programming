"""
Client class test suite
"""

import unittest

from client import Client


class TestPortNumber(unittest.TestCase):
    """
    Test suite for Client class
    """

    def test_parse_host_name_localhost(self):
        """Test parsing localhost as hostname"""
        Client.parse_hostname("localhost")

    def test_parse_host_name_ip_address(self):
        """Test parsing an IP address as hostname"""
        Client.parse_hostname("1.1.1.1")

    def test_parse_host_name_domain_name(self):
        """Test parsing a domain name as hostname"""
        Client.parse_hostname("www.duckduckgo.com")

    def test_parse_host_name_invalid(self):
        """Test parsing an invalid hostname"""
        self.assertRaises(ValueError, Client.parse_hostname, "invalid")

    def test_parse_username_valid(self):
        """Test parsing a valid username"""
        Client.parse_username("John")

    def test_parse_username_empty(self):
        """Test that parsing an empty username raises a ValueError"""
        self.assertRaises(ValueError, Client.parse_username, "")

    def test_parse_username_too_long(self):
        self.assertRaises(ValueError, Client.parse_username, "a" * 257)
        """Test that parsing a username that is too long raises a ValueError"""
