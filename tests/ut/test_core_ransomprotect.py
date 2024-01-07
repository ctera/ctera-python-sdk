from unittest import mock

# from cterasdk import exception
from cterasdk.common import Object
from cterasdk.edge import ransomprotect
from tests.ut import base_edge


class TestEdgeRansomProtect(base_edge.BaseEdgeTest):

    def test_get_configuration(self):
        self._init_filer(get_response=TestEdgeRansomProtect._get_ransom_protect_configuration_response())
        ret = ransomprotect.RansomProtect(self._filer).get_configuration()
        self._filer.get.assert_called_once_with('/config/ransomProtect/')
        self._assert_equal_objects(ret, TestEdgeRansomProtect._get_ransom_protect_configuration_response())

    def test_ransomware_is_disabled(self):
        self._init_filer(get_response=False)
        ret = ransomprotect.RansomProtect(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/ransomProtect/enabled')
        self.assertEqual(ret, True)

    def test_ransomware_is_not_disabled(self):
        self._init_filer(get_response=True)
        ret = ransomprotect.RansomProtect(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/ransomProtect/enabled')
        self.assertEqual(ret, False)

    def test_enable_ransomware_protect(self):
        self._init_filer()
        ransomprotect.RansomProtect(self._filer).enable()
        self._filer.put.assert_called_once_with('/config/ransomProtect/enabled', True)

    def test_disable_ransomware_protect(self):
        self._init_filer()
        ransomprotect.RansomProtect(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/ransomProtect/enabled', False)

    def test_modify_success(self):
        self._init_filer(get_response=TestEdgeRansomProtect._get_ransom_protect_configuration_response())
        ransomprotect.RansomProtect(self._filer).modify(True, 5, 30)
        self._filer.get.assert_called_once_with('/config/ransomProtect/')
        self._filer.put.assert_called_once_with('/config/ransomProtect/', mock.ANY)
        expected_param = TestEdgeRansomProtect._get_ransom_protect_configuration_response(True, 5, 30)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    # def test_modify_raise(self):
    #     param = Object()
    #     param.enabled = False
    #     self._init_filer(get_response=param)
    #     with self.assertRaises(exception.CTERAException) as error:
    #         ransomprotect.RansomProtect(self._filer).modify()
    #     self.assertEqual('Ransom Protect must be enabled in order to modify its configuration', error.exception.message)

    @staticmethod
    def _get_ransom_protect_configuration_response(should_block_user=None, min_num_files=None, detection_int=None):
        obj = Object()
        obj.enabled = True
        obj.shouldBlockUser = should_block_user if should_block_user is not None else False
        obj.minimalNumOfFilesForPositiveDetection = min_num_files if min_num_files is not None else 30
        obj.detectionInterval = detection_int if detection_int is not None else 10
        return obj
