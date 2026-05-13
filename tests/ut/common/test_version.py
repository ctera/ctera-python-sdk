import unittest

from cterasdk.common.utils import Version


class TestVersionUnknown(unittest.TestCase):

    def test_unknown_version_falls_back(self):
        v = Version('Unknown')
        self.assertEqual(str(v), '0.0.0')

    def test_normal_version_unchanged(self):
        v = Version('7.0.981.7')
        self.assertIn('7', str(v))
