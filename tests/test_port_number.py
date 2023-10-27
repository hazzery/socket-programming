"""
Port Number parsing class test suite.
"""

import unittest

from src.port_number import PortNumber


class TestPortNumber(unittest.TestCase):
    """
    Test suite for PortNumber class.
    """
    def test_non_numeric(self) -> None:
        """Test that non-numeric input raises a TypeError."""
        self.assertRaises(TypeError, PortNumber, "abc")

    def test_below_bound(self) -> None:
        """Test that input below the lower bound raises a ValueError."""
        self.assertRaises(ValueError, PortNumber, str(PortNumber.MINIMUM - 1))

    def test_lower_bound(self) -> None:
        """Test that input at the lower bound is accepted."""
        self.assertEqual(PortNumber.MINIMUM, PortNumber(str(PortNumber.MINIMUM)))

    def test_upper_bound(self) -> None:
        """Test that input at the upper bound is accepted."""
        self.assertEqual(PortNumber.MAXIMUM, PortNumber(str(PortNumber.MAXIMUM)))

    def test_above_bound(self) -> None:
        """Test that input above the upper bound raises a ValueError."""
        self.assertRaises(ValueError, PortNumber, str(PortNumber.MAXIMUM + 1))
