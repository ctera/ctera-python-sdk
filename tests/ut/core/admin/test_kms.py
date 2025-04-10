from unittest import mock

import munch

from cterasdk.core import kms
from tests.ut.core.admin import base_admin


class TestCoreKMS(base_admin.BaseCoreTest):  # pylint: disable=too-many-instance-attributes

    def setUp(self):
        super().setUp()
        self._kms_server_classname = 'KeyManagerServer'
        self._kms_server_name = 'kms001'
        self._kms_server_new_name = 'kms002'
        self._kms_server_ipaddr = '192.168.30.1'
        self._kms_private_key_file = './private.key'
        self._kms_private_key = 'key'
        self._kms_client_certificate_file = './client.crt'
        self._kms_client_certificate = 'client_certificate'
        self._kms_server_certificate_file = './server.crt'
        self._kms_server_certificate = 'server_certificate'
        self._kms_key_expiration = 10
        self._kms_timeout = 10
        self._kms_port = 9181

    def test_get_settings(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = kms.KMS(self._global_admin).settings()
        self._global_admin.api.get.assert_called_once_with('/settings/keyManagerSettings')
        self.assertEqual(ret, get_response)

    def test_get_status(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = kms.KMS(self._global_admin).status()
        self._global_admin.api.execute.assert_called_once_with('', 'getKeyManagerGlobalStatus')
        self.assertEqual(ret, execute_response)

    def test_enable_kms(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response, get_response=TestCoreKMS.get_default_object())
        mock_load_private_key = self.patch_call("cterasdk.lib.crypto.PrivateKey.load_private_key")
        mock_load_private_key.return_value = munch.Munch({'pem_data': self._kms_private_key.encode('utf-8')})
        mock_load_certificate = self.patch_call("cterasdk.lib.crypto.X509Certificate.load_certificate")
        mock_load_certificate.side_effect = [munch.Munch({'pem_data': self._kms_client_certificate.encode('utf-8')}),
                                             munch.Munch({'pem_data': self._kms_server_certificate.encode('utf-8')})]
        ret = kms.KMS(self._global_admin).enable(self._kms_private_key_file, self._kms_client_certificate_file,
                                                 self._kms_server_certificate_file, self._kms_key_expiration,
                                                 self._kms_timeout, self._kms_port)
        mock_load_private_key.assert_called_once_with(self._kms_private_key_file)
        mock_load_certificate.assert_has_calls(
            [
                mock.call(self._kms_client_certificate_file),
                mock.call(self._kms_server_certificate_file)
            ]
        )
        self._global_admin.api.get.assert_called_once_with('/defaults/KeyManagerSettings')
        self._global_admin.api.put.assert_called_once_with('/settings/keyManagerSettings', mock.ANY)
        expected_param = self._create_enable_kms_parameter(True)
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    @staticmethod
    def get_default_object():
        param = munch.Munch()
        param.integration = munch.Munch()
        param.integration.connectionSettings = munch.Munch()
        param.integration.tlsDetails = munch.Munch()
        param.integration.tlsDetails.files = munch.Munch()
        return param

    def _create_enable_kms_parameter(self, include_classnames=False):
        param = munch.Munch()
        param.expiration = self._kms_key_expiration
        param.integration = munch.Munch()
        param.integration.connectionSettings = munch.Munch()
        param.integration.connectionSettings.timeout = self._kms_timeout
        param.integration.connectionSettings.port = self._kms_port
        param.integration.tlsDetails = munch.Munch()
        param.integration.tlsDetails.files = munch.Munch()
        param.integration.tlsDetails.files.clientCert = self._kms_client_certificate
        param.integration.tlsDetails.files.privateKey = self._kms_private_key
        param.integration.tlsDetails.files.rootCACert = self._kms_server_certificate
        if include_classnames:
            param.integration.tlsDetails._classname = 'TLSDetails'  # pylint: disable=protected-access
            param.integration.tlsDetails.files._classname = 'TLSFiles'  # pylint: disable=protected-access
        return param

    def test_kms_modify(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response, get_response=TestCoreKMS.get_default_object())
        mock_load_private_key = self.patch_call("cterasdk.lib.crypto.PrivateKey.load_private_key")
        mock_load_private_key.return_value = munch.Munch({'pem_data': self._kms_private_key.encode('utf-8')})
        mock_load_certificate = self.patch_call("cterasdk.lib.crypto.X509Certificate.load_certificate")
        mock_load_certificate.side_effect = [munch.Munch({'pem_data': self._kms_client_certificate.encode('utf-8')}),
                                             munch.Munch({'pem_data': self._kms_server_certificate.encode('utf-8')})]
        ret = kms.KMS(self._global_admin).modify(self._kms_private_key_file, self._kms_client_certificate_file,
                                                 self._kms_server_certificate_file, self._kms_key_expiration,
                                                 self._kms_timeout, self._kms_port)
        mock_load_private_key.assert_called_once_with(self._kms_private_key_file)
        mock_load_certificate.assert_has_calls(
            [
                mock.call(self._kms_client_certificate_file),
                mock.call(self._kms_server_certificate_file)
            ]
        )
        self._global_admin.api.get.assert_called_once_with('/settings/keyManagerSettings')
        self._global_admin.api.put.assert_called_once_with('/settings/keyManagerSettings', mock.ANY)
        expected_param = self._create_enable_kms_parameter()
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_disable_kms(self):
        get_response = None
        self._init_global_admin(get_response=get_response)
        ret = kms.KMS(self._global_admin).disable()
        self._global_admin.api.execute.assert_called_once_with('', 'removeKeyManagementService')
        self.assertEqual(ret, get_response)

    def test_get_kms_server(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = kms.KMS(self._global_admin).servers.get(self._kms_server_name)
        self._global_admin.api.get.assert_called_once_with(f'/keyManagerServers/{self._kms_server_name}')
        self.assertEqual(ret, get_response)

    def test_list_all_kms_servers(self):
        with mock.patch("cterasdk.core.kms.query.iterator") as query_iterator_mock:
            kms.KMS(self._global_admin).servers.all()
            query_iterator_mock.assert_called_once_with(self._global_admin, '/keyManagerServers', mock.ANY)
            expected_query_params = base_admin.BaseCoreTest._create_query_params(  # pylint: disable=W0212
                start_from=0, count_limit=25, orFilter=True)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_add_kms_server(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = kms.KMS(self._global_admin).servers.add(self._kms_server_name, self._kms_server_ipaddr)
        self._global_admin.api.add.assert_called_once_with('/keyManagerServers', mock.ANY)
        expected_param = munch.Munch({'name': self._kms_server_name,
                                      'host': self._kms_server_ipaddr, '_classname': self._kms_server_classname})
        actual_param = self._global_admin.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_modify_kms_server(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response, get_response=munch.Munch())
        ret = kms.KMS(self._global_admin).servers.modify(self._kms_server_name, self._kms_server_new_name)
        self._global_admin.api.get.assert_called_once_with(f'/keyManagerServers/{self._kms_server_name}')
        self._global_admin.api.put.assert_called_once_with(f'/keyManagerServers/{self._kms_server_name}', mock.ANY)
        expected_param = munch.Munch({'name': self._kms_server_new_name})
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_delete_kms_server(self):
        delete_response = 'Success'
        self._init_global_admin(delete_response=delete_response)
        ret = kms.KMS(self._global_admin).servers.delete(self._kms_server_name)
        self._global_admin.api.delete.assert_called_once_with(f'/keyManagerServers/{self._kms_server_name}')
        self.assertEqual(ret, delete_response)
