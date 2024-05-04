from unittest import mock
import munch

from cterasdk.core import directoryservice
from cterasdk.core.types import UserAccount, GroupAccount, DomainControllers, AccessControlEntry, AccessControlRule 
from cterasdk.core.enum import Role, DirectoryServiceType, DirectoryServiceFetchMode
from cterasdk.common.types import ADDomainIDMapping
from cterasdk.common.object import Object
from cterasdk import exceptions
from tests.ut import base_core


class TestCoreDirectoryServices(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._tenant = 'tenant'
        self._domain_flat_name = 'DEMO'
        self._domain = 'demo.local'
        self._mapping_start = 0
        self._mapping_end = 1
        self._join_username = 'user'
        self._join_password = 'pass'
        self._domain_controllers = DomainControllers('192.168.0.1', '192.168.0.2')
        self._account_user_name = 'user'
        self._account_group_name = 'group'
        self._accounts = [UserAccount(self._account_user_name, self._domain), GroupAccount(self._account_group_name, self._domain)]
        self._acl = [AccessControlEntry(*ace) for ace in zip(self._accounts, [Role.ReadOnlyAdmin, Role.EndUser])]

    def test_disconnect(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response)
        ret = directoryservice.DirectoryService(self._global_admin).disconnect()
        self._global_admin.api.put.assert_called_once_with('/directoryConnector', None)
        self.assertEqual(ret, put_response)

    def test_get_default_role(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = directoryservice.DirectoryService(self._global_admin).get_default_role()
        self._global_admin.api.get.assert_called_once_with('/directoryConnector/noMatchRole')
        self.assertEqual(ret, get_response)

    def test_get_connected_domain_success(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = directoryservice.DirectoryService(self._global_admin).get_connected_domain()
        self._global_admin.api.get.assert_called_once_with('/directoryConnector/domain')
        self.assertEqual(ret, get_response)

    def test_get_connected_domain_failure(self):
        self._global_admin.api.get = mock.MagicMock(side_effect=exceptions.CTERAException())
        ret = directoryservice.DirectoryService(self._global_admin).get_connected_domain()
        self._global_admin.api.get.assert_called_once_with('/directoryConnector/domain')
        self.assertEqual(ret, None)

    def test_domains(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = directoryservice.DirectoryService(self._global_admin).domains()
        self._global_admin.api.execute.assert_called_once_with('', 'getADTrustedDomains', False)
        self.assertEqual(ret, execute_response)

    def test_get_advanced_mapping(self):
        get_response = [munch.Munch({'domainFlatName': self._domain_flat_name})]
        self._init_global_admin(get_response=get_response)
        ret = directoryservice.DirectoryService(self._global_admin).get_advanced_mapping()
        self._global_admin.api.get.assert_called_once_with('/directoryConnector/idMapping/map')
        self.assertEqual(ret[self._domain_flat_name], get_response[0])

    def test_set_advanced_mapping(self):
        put_response = 'Success'
        self._init_global_admin(get_response=[], put_response=put_response)
        mapping = ADDomainIDMapping(self._domain, self._mapping_start, self._mapping_end)
        ret = directoryservice.DirectoryService(self._global_admin).set_advanced_mapping([mapping])
        self._global_admin.api.get.assert_called_once_with('/directoryConnector')
        self._global_admin.api.put.assert_called_once_with('/directoryConnector/idMapping', mock.ANY)
        expected_param = TestCoreDirectoryServices._create_mapping_param([mapping])
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_connected_disconnected(self):
        self._init_global_admin(get_response=None)
        ret = directoryservice.DirectoryService(self._global_admin).connected()
        self._global_admin.api.get.assert_called_once_with('/directoryConnector')
        self.assertEqual(ret, False)

    def test_connected_failure(self):
        get_response = 'settings'
        self._init_global_admin(get_response=get_response)
        self._global_admin.api.execute = mock.MagicMock(side_effect=exceptions.CTERAException())
        ret = directoryservice.DirectoryService(self._global_admin).connected()
        self._global_admin.api.get.assert_called_once_with('/directoryConnector')
        self._global_admin.api.execute.assert_called_once_with('', 'testAndSaveAD', get_response)
        self.assertEqual(ret, False)

    def test_connected_success(self):
        get_response = 'settings'
        self._init_global_admin(get_response=get_response, execute_response=None)
        ret = directoryservice.DirectoryService(self._global_admin).connected()
        self._global_admin.api.get.assert_called_once_with('/directoryConnector')
        self._global_admin.api.execute.assert_called_once_with('', 'testAndSaveAD', get_response)
        self.assertEqual(ret, True)

    def test_fetch_users_groups_success(self):
        mock_search_users = self.patch_call("cterasdk.core.directoryservice.DirectoryService._search_users")
        mock_search_groups = self.patch_call("cterasdk.core.directoryservice.DirectoryService._search_groups")
        get_response = [self._domain]
        execute_response = 'Success'
        self._init_global_admin(get_response=get_response, execute_response=execute_response)
        ret = directoryservice.DirectoryService(self._global_admin).fetch(self._accounts)
        mock_search_users.assert_called_once_with(self._domain, self._account_user_name)
        mock_search_groups.assert_called_once_with(self._domain, self._account_group_name)
        self._global_admin.api.execute.assert_called_once_with('', 'syncAD', mock.ANY)
        self.assertEqual(ret, execute_response)

    def test_connect(self):
        mock_session = self.patch_call("cterasdk.objects.services.Management.session")
        mock_session.return_value = munch.Munch({'user': munch.Munch({'tenant': self._tenant})})
        self._init_global_admin()
        directoryservice.DirectoryService(self._global_admin).connect(self._domain, self._join_username,
                                                                            self._join_password,
                                                                            domain_controllers=self._domain_controllers)
        self._global_admin.api.execute.assert_called_once_with('', 'testAndSaveAD', mock.ANY)
        expected_param = self._create_connect_to_directory_services_param(domain_controllers=self._domain_controllers)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def _create_connect_to_directory_services_param(self, domain_controllers=None):
        param = Object()
        param._classname = 'ActiveDirectory'  # pylint: disable=protected-access
        param.type = DirectoryServiceType.Microsoft
        param.domain = self._domain
        param.useKerberos = False
        param.useSSL = False
        param.username = self._join_username
        param.password = self._join_password
        param.ou = None
        param.noMatchRole = Role.Disabled
        param.accessControlRules = None
        param.idMapping = None
        param.fetchMode = DirectoryServiceFetchMode.Lazy
        param.ipAddresses = None

        if domain_controllers:
            param.ipAddresses = Object()
            param.ipAddresses._classname = 'DomainControlIPAddresses'  # pylint: disable=protected-access
            param.ipAddresses.ipAddress1 = domain_controllers.primary
            param.ipAddresses.ipAddress2 = domain_controllers.secondary        
        return param

    def test_set_access_control_disconnected(self):
        self._init_global_admin()
        with self.assertRaises(exceptions.CTERAException) as error:
            directoryservice.DirectoryService(self._global_admin).set_access_control(self._acl)
        self.assertEqual('Failed to apply access control. Not connected to directory services.', 
                         error.exception.message)
    
    def test_set_access_control_with_default(self):
        mock_search_users = self.patch_call("cterasdk.core.directoryservice.DirectoryService._search_users")
        mock_search_users.return_value = self._account_user_name
        mock_search_groups = self.patch_call("cterasdk.core.directoryservice.DirectoryService._search_groups")
        mock_search_groups.return_value = self._account_group_name
        get_response = munch.Munch()
        put_response = 'Success'
        self._init_global_admin(get_response=get_response, put_response=put_response)
        ret = directoryservice.DirectoryService(self._global_admin).set_access_control(self._acl, Role.Disabled)
        self._global_admin.api.get.assert_called_once_with('/directoryConnector')
        self._global_admin.api.put.assert_has_calls(
            [
                mock.call('/directoryConnector/accessControlRules', mock.ANY),
                mock.call('/directoryConnector/noMatchRole', Role.Disabled)
            ]
        )
        self.assertEqual(ret, put_response)

    @staticmethod
    def _create_mapping_param(mapping):
        param = Object()
        param._classname = 'ADIDMapping'  # pylint: disable=protected-access
        param.map = mapping
        return param
