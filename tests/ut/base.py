import unittest
from .common import utilities


class BaseTest(unittest.TestCase):

    def patch_call(self, module_path, **patch_kwargs):
        return utilities.patch_call(self, module_path, **patch_kwargs)

    def patch_property(self, module_path, **patch_kwargs):
        return utilities.patch_property(self, module_path, **patch_kwargs)

    def _assert_equal_objects(self, actual_param, expected_param):
        return utilities.assert_equal_objects(self, actual_param, expected_param)
