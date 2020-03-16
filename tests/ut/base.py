import queue
import unittest

from cterasdk.common import Object


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
        q = queue.Queue()
        q.put((actual_param, expected_param))
        while not q.empty():
            actual_param, expected_param = q.get()
            for field in [a for a in dir(actual_param) if not a.startswith('__')]:
                actual_param_attr = getattr(actual_param, field)
                if isinstance(actual_param_attr, Object):
                    q.put((actual_param_attr, getattr(expected_param, field)))
                else:
                    self.assertEqual(actual_param_attr, getattr(expected_param, field))
