"""Client class test suite."""

import pytest

from src.parse_hostname import parse_hostname
from src.parse_username import parse_username


def test_parse_host_name_localhost() -> None:
    """Test parsing localhost as hostname."""
    parse_hostname("localhost")


def test_parse_host_name_ip_address() -> None:
    """Test parsing a valid IP address as hostname."""
    parse_hostname("1.1.1.1")


def test_parse_host_name_domain_name() -> None:
    """Test parsing a domain name as hostname."""
    parse_hostname("www.duckduckgo.com")


def test_parse_host_name_invalid() -> None:
    """Test parsing an invalid hostname."""
    with pytest.raises(
        ValueError,
        match='Invalid host name, must be an IP address, domain name, or "localhost"',
    ):
        parse_hostname("invalid")


def test_parse_host_name_invalid_ip() -> None:
    """Test parsing an invalid IP address as hostname."""
    with pytest.raises(
        ValueError,
        match='Invalid host name, must be an IP address, domain name, or "localhost"',
    ):
        parse_hostname("256.0.0.1")


def test_parse_username_min_length() -> None:
    """Test parsing a valid username with minimum length."""
    parse_username("J")


def test_parse_username_max_length() -> None:
    """Test parsing a valid username with maximum length."""
    parse_username("J" * 255)


def test_parse_username_empty() -> None:
    """Test that parsing an empty username raises a ValueError."""
    with pytest.raises(
        ValueError,
        match="Username must not be empty",
    ):
        parse_username("")


def test_parse_username_too_long() -> None:
    """Test that parsing a username that is too long raises a ValueError."""
    with pytest.raises(
        ValueError,
        match="Username must consume at most 255 bytes",
    ):
        parse_username("a" * 256)
