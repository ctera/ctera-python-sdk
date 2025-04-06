import unittest
from ..common import utilities


class BaseAsyncTest(unittest.IsolatedAsyncioTestCase):
    """Base Async Test"""

    def assert_equal_objects(self, actual_param, expected_param):
        return utilities.assert_equal_objects(self, actual_param, expected_param)