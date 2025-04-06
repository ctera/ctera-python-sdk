from unittest import mock

from cterasdk.common import Object
from cterasdk.core import antivirus
from cterasdk.core.enum import ICAPServices
from tests.ut.core.admin import base_admin


class TestCoreAntivirus(base_admin.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._name = 'av-server-name'
        self._type = ICAPServices.Antivirus
        self._url = 'https://virus:1234/signature'

    def test_rescan(self):
        self._init_global_admin()
        antivirus.Antivirus(self._global_admin).rescan()
        self._global_admin.api.execute.assert_called_once_with('/servers', 'resetAllAVBG')

    def test_suspend(self):
        self._init_global_admin()
        antivirus.Antivirus(self._global_admin).suspend()
        self._global_admin.api.put.assert_called_once_with('/settings/cloudFSSettings/antivirusSettings/isEnabled', False)

    def test_unsuspend(self):
        self._init_global_admin()
        antivirus.Antivirus(self._global_admin).unsuspend()
        self._global_admin.api.put.assert_called_once_with('/settings/cloudFSSettings/antivirusSettings/isEnabled', True)

    def test_status(self):
        self._init_global_admin()
        antivirus.Antivirus(self._global_admin).status()
        self._global_admin.api.execute.assert_called_once_with('', 'getIcapGlobalStatus', mock.ANY)
        expected_param = Object()
        expected_param.icapService = ICAPServices.Antivirus
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_get_server(self):
        self._init_global_admin()
        antivirus.AntivirusServers(self._global_admin).get(self._name)
        self._global_admin.api.get.assert_called_once_with(f'/antiviruses/{self._name}')

    def test_add_server(self):
        self._init_global_admin()
        antivirus.AntivirusServers(self._global_admin).add(self._name, self._type, self._url)
        self._global_admin.api.add.assert_called_once_with('/antiviruses', mock.ANY)
        expected_param = self._create_antivirus_param()
        actual_param = self._global_admin.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def _create_antivirus_param(self, connection_timeout=5):
        param = Object()
        param._classname = 'Antivirus'  # pylint: disable=protected-access
        param.name = self._name
        param.type = self._type
        param.serverUrl = self._url
        param.connectionTimeoutSeconds = connection_timeout
        return param

    def test_delete_server(self):
        self._init_global_admin()
        antivirus.AntivirusServers(self._global_admin).delete(self._name)
        self._global_admin.api.delete.assert_called_once_with(f'/antiviruses/{self._name}')

    def test_suspend_server(self):
        self._init_global_admin()
        antivirus.AntivirusServers(self._global_admin).suspend(self._name)
        self._global_admin.api.put.assert_called_once_with(f'/antiviruses/{self._name}/enabled', False)

    def test_unsuspend_server(self):
        self._init_global_admin()
        antivirus.AntivirusServers(self._global_admin).unsuspend(self._name)
        self._global_admin.api.put.assert_called_once_with(f'/antiviruses/{self._name}/enabled', True)
