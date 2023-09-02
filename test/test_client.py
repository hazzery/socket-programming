import unittest

from client import Client


class TestPortNumber(unittest.TestCase):

    def test_parse_host_name_localhost(self):
        Client.parse_hostname("localhost")

    def test_parse_host_name_ip_address(self):
        Client.parse_hostname("1.1.1.1")

    def test_parse_host_name_domain_name(self):
        Client.parse_hostname("www.duckduckgo.com")

    def test_parse_host_name_invalid(self):
        self.assertRaises(ValueError, Client.parse_hostname, "invalid")

    def test_parse_username_valid(self):
        Client.parse_username("John")

    def test_parse_username_empty(self):
        self.assertRaises(ValueError, Client.parse_username, "")

    def test_parse_username_too_long(self):
        self.assertRaises(ValueError, Client.parse_username, "a" * 257)
