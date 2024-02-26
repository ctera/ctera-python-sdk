from unittest import mock
import munch

from cterasdk.core import directoryservice
from cterasdk.common.types import ADDomainIDMapping
from cterasdk.common.object import Object
from cterasdk import exceptions
from tests.ut import base_core


class TestCoreDirectoryServices(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._domain_flat_name = 'DEMO'
        self._domain = 'demo.local'
        self._mapping_start = 0
        self._mapping_end = 1

    def test_disconnect(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response)
        ret = directoryservice.DirectoryService(self._global_admin).disconnect()
        self._global_admin.put.assert_called_once_with('/directoryConnector', None)
        self.assertEqual(ret, put_response)

    def test_get_default_role(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = directoryservice.DirectoryService(self._global_admin).get_default_role()
        self._global_admin.get.assert_called_once_with('/directoryConnector/noMatchRole')
        self.assertEqual(ret, get_response)

    def test_get_connected_domain_success(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = directoryservice.DirectoryService(self._global_admin).get_connected_domain()
        self._global_admin.get.assert_called_once_with('/directoryConnector/domain')
        self.assertEqual(ret, get_response)

    def test_get_connected_domain_failure(self):
        self._global_admin.get = mock.MagicMock(side_effect=exceptions.CTERAException())
        ret = directoryservice.DirectoryService(self._global_admin).get_connected_domain()
        self._global_admin.get.assert_called_once_with('/directoryConnector/domain')
        self.assertEqual(ret, None)

    def test_domains(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = directoryservice.DirectoryService(self._global_admin).domains()
        self._global_admin.execute.assert_called_once_with('', 'getADTrustedDomains', False)
        self.assertEqual(ret, execute_response)

    def test_get_advanced_mapping(self):
        get_response = [munch.Munch({'domainFlatName': self._domain_flat_name})]
        self._init_global_admin(get_response=get_response)
        ret = directoryservice.DirectoryService(self._global_admin).get_advanced_mapping()
        self._global_admin.get.assert_called_once_with('/directoryConnector/idMapping/map')
        self.assertEqual(ret[self._domain_flat_name], get_response[0])

    def test_set_advanced_mapping(self):
        put_response = 'Success'
        self._init_global_admin(get_response=[], put_response=put_response)
        mapping = ADDomainIDMapping(self._domain, self._mapping_start, self._mapping_end)
        ret = directoryservice.DirectoryService(self._global_admin).set_advanced_mapping([mapping])
        self._global_admin.get.assert_called_once_with('/directoryConnector')
        self._global_admin.put.assert_called_once_with('/directoryConnector/idMapping', mock.ANY)
        expected_param = TestCoreDirectoryServices._create_mapping_param([mapping])
        actual_param = self._global_admin.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_connected_disconnected(self):
        self._init_global_admin(get_response=None)
        ret = directoryservice.DirectoryService(self._global_admin).connected()
        self._global_admin.get.assert_called_once_with('/directoryConnector')
        self.assertEqual(ret, False)

    def test_connected_failure(self):
        get_response = 'settings'
        self._init_global_admin(get_response=get_response)
        self._global_admin.execute = mock.MagicMock(side_effect=exceptions.CTERAException())
        ret = directoryservice.DirectoryService(self._global_admin).connected()
        self._global_admin.get.assert_called_once_with('/directoryConnector')
        self._global_admin.execute.assert_called_once_with('', 'testAndSaveAD', get_response)
        self.assertEqual(ret, False)

    def test_connected_success(self):
        get_response = 'settings'
        self._init_global_admin(get_response=get_response, execute_response=None)
        ret = directoryservice.DirectoryService(self._global_admin).connected()
        self._global_admin.get.assert_called_once_with('/directoryConnector')
        self._global_admin.execute.assert_called_once_with('', 'testAndSaveAD', get_response)
        self.assertEqual(ret, True)

    @staticmethod
    def _create_mapping_param(mapping):
        param = Object()
        param._classname = 'ADIDMapping'  # pylint: disable=protected-access
        param.map = mapping
        return param
