"""
Port Number parsing class test suite.
"""

import unittest

from src.port_number import PortNumber


class TestPortNumber(unittest.TestCase):
    """
    Test suite for PortNumber class.
    """

    def test_non_numeric(self):
        """Test that non-numeric input raises a TypeError."""
        self.assertRaises(TypeError, PortNumber, 'abc')

    def test_below_bound(self):
        """Test that input below the lower bound raises a ValueError."""
        self.assertRaises(ValueError, PortNumber, str(PortNumber.MINIMUM - 1))

    def test_lower_bound(self):
        self.assertEquals(PortNumber.MINIMUM, PortNumber(str(PortNumber.MINIMUM)))
        """Test that input at the lower bound is accepted."""

    def test_upper_bound(self):
        self.assertEquals(PortNumber.MAXIMUM, PortNumber(str(PortNumber.MAXIMUM)))
        """Test that input at the upper bound is accepted."""

    def test_above_bound(self):
        """Test that input above the upper bound raises a ValueError."""
        self.assertRaises(ValueError, PortNumber, str(PortNumber.MAXIMUM + 1))

