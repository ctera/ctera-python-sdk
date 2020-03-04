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
