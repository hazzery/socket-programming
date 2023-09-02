import unittest

from src.port_number import PortNumber


class TestPortNumber(unittest.TestCase):

    def test_non_numeric(self):
        self.assertRaises(TypeError, PortNumber, 'abc')

    def test_below_bound(self):
        self.assertRaises(ValueError, PortNumber, str(PortNumber.MINIMUM - 1))

    def test_lower_bound(self):
        self.assertEquals(PortNumber.MINIMUM, PortNumber(str(PortNumber.MINIMUM)))

    def test_upper_bound(self):
        self.assertEquals(PortNumber.MAXIMUM, PortNumber(str(PortNumber.MAXIMUM)))

    def test_above_bound(self):
        self.assertRaises(ValueError, PortNumber, str(PortNumber.MAXIMUM + 1))

