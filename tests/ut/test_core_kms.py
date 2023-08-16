from unittest import mock

import munch

from cterasdk.core import kms
from tests.ut import base_core


class TestCoreKMS(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._kms_server_classname = 'KeyManagerServer'
        self._kms_server_name = 'kms001'
        self._kms_server_ipaddr = '192.168.30.1'

    def test_get_settings(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = kms.KMS(self._global_admin).settings()
        self._global_admin.get.assert_called_once_with('/settings/keyManagerSettings')
        self.assertEqual(ret, get_response)

    def test_get_status(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = kms.KMS(self._global_admin).status()
        self._global_admin.execute.assert_called_once_with('', 'getKeyManagerGlobalStatus')
        self.assertEqual(ret, execute_response)

    def test_add_kms_server(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = kms.KMS(self._global_admin).servers.add(self._kms_server_name, self._kms_server_ipaddr)
        self._global_admin.add.assert_called_once_with('/keyManagerServers', mock.ANY)
        expected_param = munch.Munch({'name': self._kms_server_name,
                                      'host': self._kms_server_ipaddr, '_classname': self._kms_server_classname})
        actual_param = self._global_admin.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_delete_kms_server(self):
        delete_response = 'Success'
        self._init_global_admin(delete_response=delete_response)
        ret = kms.KMS(self._global_admin).servers.delete(self._kms_server_name)
        self._global_admin.delete.assert_called_once_with(f'/keyManagerServers/{self._kms_server_name}')
        self.assertEqual(ret, delete_response)

    def test_get_kms_server(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = kms.KMS(self._global_admin).servers.get(self._kms_server_name)
        self._global_admin.get.assert_called_once_with(f'/keyManagerServers/{self._kms_server_name}')
        self.assertEqual(ret, get_response)
