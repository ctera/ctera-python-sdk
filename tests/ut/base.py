import unittest


class BaseTest(unittest.TestCase):

    def patch_call(self, module_path, **patch_kwargs):
        """Mock patch a given path as a call and schedule proper mock cleanup."""
        call_patcher = unittest.mock.patch(module_path, **patch_kwargs)
        self.addCleanup(call_patcher.stop)
        return call_patcher.start()

    def patch_property(self, module_path, **patch_kwargs):
        """Mock patch a given path as a property and schedule proper mock cleanup."""
        patch_kwargs.update({'new_callable': unittest.mock.PropertyMock})
        return self.patch_call(module_path, **patch_kwargs)

    def _assert_equal_objects(self, expected_param, actual_param):
        for field in [a for a in dir(actual_param) if not a.startswith('__')]:
            self.assertEqual(getattr(actual_param, field), getattr(expected_param, field))
