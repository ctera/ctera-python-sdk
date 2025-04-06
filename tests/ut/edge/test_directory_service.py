from unittest import mock

from cterasdk import exceptions
from cterasdk.edge import directoryservice
from cterasdk.edge.types import TCPService, TCPConnectResult
from cterasdk.common import Object
from cterasdk.lib import task_manager_base
from tests.ut.edge import base_edge


class TestEdgeDirectoryService(base_edge.BaseEdgeTest):  # pylint: disable=too-many-instance-attributes

    def setUp(self):
        super().setUp()
        self._domain = "ctera.local"
        self._username = 'admin'
        self._password = 'password'
        self._workgroup = "CTERA"
        self._domain_flat_name = "CTERA"
        self._mapping_min = 2000000
        self._mapping_max = 5000000
        self._dc = '192.168.0.1'
        self._ports = [389, 3268, 445]

        self._task_id = '138'
        self._ldap_port = 389
        self._ldap_service = TCPService(self._domain, self._ldap_port)

    def test_connected(self):
        self._init_filer(get_response=0)
        ret = directoryservice.DirectoryService(self._filer).connected()
        self.assertTrue(ret)

    def test_disconnected(self):
        self._init_filer(get_response=-1)
        ret = directoryservice.DirectoryService(self._filer).connected()
        self.assertFalse(ret)

    def test_connect(self):
        self._init_filer()
        get_response_side_effect = TestEdgeDirectoryService._get_response_side_effect(self._get_workgroup_param(), None)
        self._filer.api.get = mock.MagicMock(side_effect=get_response_side_effect)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._domain, self._ldap_port, True))

        directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password, check_connection=True)

        self._filer.network.tcp_connect.assert_called_once_with(self._ldap_service)
        self._filer.api.get.assert_has_calls([
            mock.call('/config/fileservices/cifs/passwordServer'),
            mock.call('/config/fileservices/cifs')
        ])
        self._filer.api.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_domain_param()
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.api.execute.assert_called_once_with("/status/fileservices/cifs", "joinDomain", mock.ANY)
        expected_param = self._get_domain_join_param()
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_connect_with_ou_path(self):
        self._init_filer()
        ou_path = "ou=North America,DC=ctera,DC=local"
        get_response_side_effect = TestEdgeDirectoryService._get_response_side_effect(self._get_workgroup_param(), None)
        self._filer.api.get = mock.MagicMock(side_effect=get_response_side_effect)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._domain, self._ldap_port, True))

        directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password, ou_path, check_connection=True)

        self._filer.network.tcp_connect.assert_called_once_with(self._ldap_service)
        self._filer.api.get.assert_has_calls([
            mock.call('/config/fileservices/cifs/passwordServer'),
            mock.call('/config/fileservices/cifs')
        ])
        self._filer.api.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_domain_param()
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.api.execute.assert_called_once_with("/status/fileservices/cifs", "joinDomain", mock.ANY)
        expected_param = self._get_domain_join_param(ou_path)
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_connect_failure_no_connection_over_port(self):
        get_response = self._get_workgroup_param()
        self._init_filer(get_response=get_response)

        expected_exception = exceptions.CTERAException()
        self._filer.api.execute = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException):
            directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password)

    def test_connect_join_failure(self):
        self._init_filer()
        get_response_side_effect = TestEdgeDirectoryService._get_response_side_effect(self._get_workgroup_param(), None)
        self._filer.api.get = mock.MagicMock(side_effect=get_response_side_effect)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._domain, self._ldap_port, True))
        self._filer.api.execute = mock.MagicMock(side_effect=task_manager_base.TaskError(self._task_id))

        with self.assertRaises(exceptions.CTERAException):
            directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password, check_connection=True)

        self._filer.network.tcp_connect.assert_called_once_with(self._ldap_service)

        self._filer.api.get.assert_has_calls([
            mock.call('/config/fileservices/cifs/passwordServer'),
            mock.call('/config/fileservices/cifs')
        ])

        self._filer.api.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)
        expected_param = self._get_domain_param()
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.api.execute.assert_called_once_with("/status/fileservices/cifs", "joinDomain", mock.ANY)
        expected_param = self._get_domain_join_param()
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_connect_connection_error(self):
        self._init_filer(get_response=None)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._domain, self._ldap_port, False))

        with self.assertRaises(ConnectionError) as error:
            directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password, check_connection=True)

        self._filer.api.get.assert_called_once_with('/config/fileservices/cifs/passwordServer')
        self._filer.network.tcp_connect.assert_called_once_with(self._ldap_service)
        self.assertEqual(f'Unable to establish LDAP connection {self._domain}:{self._ldap_port}', str(error.exception))

    def test_get_advanced_mapping(self):
        get_response = [TestEdgeDirectoryService._get_advanced_mapping_object(self._domain_flat_name, 0, 0)]
        self._init_filer(get_response=get_response)
        ret = directoryservice.DirectoryService(self._filer).get_advanced_mapping()
        self._filer.api.get.assert_called_once_with('/config/fileservices/cifs/idMapping/map')
        self._assert_equal_objects(ret[self._domain_flat_name], get_response[0])

    def test_set_advanced_mapping(self):
        execute_response = TestEdgeDirectoryService._create_get_domains_response(self._domain_flat_name)
        advanced_mapping = [
            TestEdgeDirectoryService._get_advanced_mapping_object(self._domain_flat_name, self._mapping_min, self._mapping_max)
        ]
        self._init_filer(get_response=0, execute_response=execute_response)
        directoryservice.DirectoryService(self._filer).set_advanced_mapping(advanced_mapping)
        self._filer.api.get.assert_has_calls([
            mock.call('/status/fileservices/cifs/joinStatus'),
            mock.call('/config/fileservices/cifs/idMapping/map')
        ])
        self._filer.api.execute.assert_called_once_with('/status/fileservices/cifs', 'enumDiscoveredDomains')
        self._filer.api.put.assert_called_once_with('/config/fileservices/cifs/idMapping/map', mock.ANY)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(advanced_mapping[0], actual_param[0])

    def test_set_advanced_mapping_raise(self):
        self._init_filer(get_response=1)
        with self.assertRaises(exceptions.CTERAException) as error:
            directoryservice.DirectoryService(self._filer).set_advanced_mapping([])
        self.assertEqual('Failed to configure advanced mapping. Not connected to directory services.', error.exception.message)

    def test_domains(self):
        self._init_filer(execute_response=TestEdgeDirectoryService._create_get_domains_response(self._domain_flat_name))
        ret = directoryservice.DirectoryService(self._filer).domains()
        self._filer.api.execute.assert_called_once_with('/status/fileservices/cifs', 'enumDiscoveredDomains')
        self.assertEqual(ret[0], self._domain_flat_name)

    @staticmethod
    def _create_get_domains_response(*domains):
        param = []
        for domain_name in domains:
            domain = Object()
            domain.flatName = domain_name
            param.append(domain)
        return param

    def test_disconnect(self):
        get_response = self._get_domain_param()
        self._init_filer(get_response=get_response)
        directoryservice.DirectoryService(self._filer).disconnect()
        self._filer.api.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.api.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_workgroup_param()
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_get_connected_domain(self):
        obj = Object()
        obj.type = 'domain'
        obj.domain = self._domain
        obj.workgroup = None
        self._init_filer(get_response=obj)
        ret = directoryservice.DirectoryService(self._filer).get_connected_domain()
        self._filer.api.get.assert_called_once_with('/config/fileservices/cifs')
        self._assert_equal_objects(ret, obj)

    def test_get_static_domain_controller(self):
        self._init_filer(get_response=self._dc)
        ret = directoryservice.DirectoryService(self._filer).get_static_domain_controller()
        self._filer.api.get.assert_called_once_with('/config/fileservices/cifs/passwordServer')
        self.assertEqual(ret, self._dc)

    def test_set_static_domain_controller(self):
        self._init_filer(put_response=self._dc)
        ret = directoryservice.DirectoryService(self._filer).set_static_domain_controller(self._dc)
        self._filer.api.put.assert_called_once_with('/config/fileservices/cifs/passwordServer', self._dc)
        self.assertEqual(ret, self._dc)

    def test_remove_static_domain_controller(self):
        self._init_filer()
        directoryservice.DirectoryService(self._filer).remove_static_domain_controller()
        self._filer.api.put.assert_called_once_with('/config/fileservices/cifs/passwordServer', None)

    @staticmethod
    def _get_advanced_mapping_object(domain_flat_name, min_id, max_id):
        mapping = Object()
        mapping.domainFlatName = domain_flat_name
        mapping.minID = min_id
        mapping.maxID = max_id
        return mapping

    def _get_domain_join_param(self, ou=None):
        o = Object()
        o.username = self._username
        o.password = self._password
        if ou is not None:
            o.ouPath = ou
        return o

    def _get_domain_param(self):
        cifs_param = Object()
        cifs_param.type = "domain"
        cifs_param.workgroup = None
        cifs_param.domain = self._domain
        return cifs_param

    def _get_workgroup_param(self):
        cifs_param = Object()
        cifs_param.type = "workgroup"
        cifs_param.workgroup = self._workgroup
        cifs_param.domain = None
        return cifs_param

    @staticmethod
    def _get_response_side_effect(cifs_param, domain_controllers):
        def get_response(path):
            if path == '/config/fileservices/cifs/passwordServer':
                return domain_controllers
            if path == '/config/fileservices/cifs':
                return cifs_param
            return None
        return get_response
