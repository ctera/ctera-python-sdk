import munch
from unittest import mock

from cterasdk import exception
from cterasdk.edge import ransom_protect
from tests.ut import base_edge


class TestEdgeRansomProtect(base_edge.BaseEdgeTest):

    def test_get_ransom_protect_configuration(self):
        get_response = TestEdgeRansomProtect._get_ransom_protect_config()
        self._init_filer(get_response=get_response)
        ret = ransom_protect.RansomProtect(self._filer).get_configuration()
        self._filer.get.assert_called_once_with('/config/ransomProtect/')
        self._assert_equal_objects(ret, get_response)

    def test_ransom_protect_is_disabled(self):
        self._init_filer(get_response=False)
        ret = ransom_protect.RansomProtect(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/ransomProtect/enabled')
        self.assertEqual(ret, True)

    def test_ransom_protect_is_enabled(self):
        self._init_filer(get_response=True)
        ret = ransom_protect.RansomProtect(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/ransomProtect/enabled')
        self.assertEqual(ret, False)

    def test_enable_ransom_protect(self):
        self._init_filer()
        ransom_protect.RansomProtect(self._filer).enable()
        self._filer.put.assert_called_once_with('/config/ransomProtect/enabled', True)

    def test_disable_ransom_protect(self):
        self._init_filer()
        ransom_protect.RansomProtect(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/ransomProtect/enabled', False)

    def test_modify_success(self):
        self._init_filer(get_response=TestEdgeRansomProtect._get_ransom_protect_config())
        ransom_protect.RansomProtect(self._filer).modify(True, 5, 30)
        self._filer.get.assert_called_once_with('/config/ransomProtect/')
        self._filer.put.assert_called_once_with('/config/ransomProtect/', mock.ANY)
        expected_param = TestEdgeRansomProtect._get_ransom_protect_config(True, 5, 30)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_raise(self):
        get_response = munch.Munch({'enabled': False})
        self._init_filer(get_response=get_response)
        with self.assertRaises(exception.CTERAException) as error:
            ransom_protect.RansomProtect(self._filer).modify()
        self.assertEqual('Ransom Protect must be enabled to modify its configuration', error.exception.message)

    @staticmethod
    def _get_ransom_protect_config(block_users=None, detection_threshold=None, detection_interval=None):
        obj = munch.Munch({
            'shouldBlockUser': block_users if block_users is not None else False,
            'minimalNumOfFilesForPositiveDetection': detection_threshold if detection_threshold is not None else 30,
            'detectionInterval': detection_interval if detection_interval is not None else 10
        })
        return obj
