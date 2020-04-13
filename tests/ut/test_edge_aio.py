from unittest import mock

from cterasdk.edge import aio
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeAIO(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._disable_aio = (False, 0, 0)
        self._enable_aio = (True, 1, 1)

    def test_is_enabled_true(self):
        get_response = self._get_cifs_object(True)
        self._init_filer(get_response=get_response)
        ret = aio.AIO(self._filer).is_enabled()
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self.assertEqual(ret, True)

    def test_is_enabled_false(self):
        get_response = self._get_cifs_object(False)
        self._init_filer(get_response=get_response)
        ret = aio.AIO(self._filer).is_enabled()
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self.assertEqual(ret, False)

    def test_disable_aio(self):
        get_response = self._get_cifs_object(enable_aio=True)
        self._init_filer(get_response=get_response)
        aio.AIO(self._filer).disable()
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_cifs_object(enable_aio=False)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_aio(self):
        get_response = self._get_cifs_object(enable_aio=False)
        self._init_filer(get_response=get_response)
        aio.AIO(self._filer).enable()
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_cifs_object(enable_aio=True)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def _get_cifs_object(self, enable_aio):
        robust_mutexes, aio_read_threshold, aio_write_threshold = self._enable_aio if enable_aio else self._disable_aio
        cifs_param = Object()
        cifs_param.robustMutexes = robust_mutexes
        cifs_param.aioReadThreshold = aio_read_threshold
        cifs_param.aioWriteThreshold = aio_write_threshold
        return cifs_param
