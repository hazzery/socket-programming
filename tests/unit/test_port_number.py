"""Port Number parsing class test suite."""

import re

import pytest

from src.port_number import PortNumber


def test_non_numeric() -> None:
    """Test that non-numeric input raises a TypeError."""
    with pytest.raises(TypeError):
        PortNumber("abc")


def test_below_bound() -> None:
    """Test that input below the lower bound raises a ValueError."""
    with pytest.raises(
        ValueError,
        match=re.escape("Port number must be in the range 1024-64000 (inclusive)"),
    ):
        PortNumber(str(PortNumber.MINIMUM - 1))


def test_lower_bound() -> None:
    """Test that input at the lower bound is accepted."""
    assert PortNumber(str(PortNumber.MINIMUM)) == PortNumber.MINIMUM


def test_upper_bound() -> None:
    """Test that input at the upper bound is accepted."""
    assert PortNumber(str(PortNumber.MAXIMUM)) == PortNumber.MAXIMUM


def test_above_bound() -> None:
    """Test that input above the upper bound raises a ValueError."""
    with pytest.raises(
        ValueError,
        match=re.escape("Port number must be in the range 1024-64000 (inclusive)"),
    ):
        PortNumber(str(PortNumber.MAXIMUM + 1))
