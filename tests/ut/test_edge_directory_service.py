from unittest import mock

from cterasdk import exception
from cterasdk.edge import directoryservice
from cterasdk.edge.types import TCPService, TCPConnectResult
from cterasdk.common import Object
from cterasdk.lib import task_manager_base
from tests.ut import base_edge


class TestEdgeDirectoryService(base_edge.BaseEdgeTest):

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

    def test_connect(self):
        get_response = self._get_workgroup_param()
        self._init_filer(get_response=get_response)
        tcp_connect_return_value = TCPConnectResult(self._domain, self._ldap_port, True)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=tcp_connect_return_value)

        directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password)

        self._filer.network.tcp_connect.assert_called_once_with(self._ldap_service)
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_domain_param()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.execute.assert_called_once_with("/status/fileservices/cifs", "joinDomain", mock.ANY)
        expected_param = self._get_domain_join_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_connect_with_ou_path(self):
        ou_path = "ou=North America,DC=ctera,DC=local"
        get_response = self._get_workgroup_param()
        self._init_filer(get_response=get_response)
        tcp_connect_return_value = TCPConnectResult(self._domain, self._ldap_port, True)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=tcp_connect_return_value)

        directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password, ou_path)

        self._filer.network.tcp_connect.assert_called_once_with(self._ldap_service)
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_domain_param()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.execute.assert_called_once_with("/status/fileservices/cifs", "joinDomain", mock.ANY)
        expected_param = self._get_domain_join_param(ou_path)
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_connect_failure_no_connection_over_port(self):
        get_response = self._get_workgroup_param()
        self._init_filer(get_response=get_response)

        expected_exception = exception.CTERAException()
        self._filer.execute = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException):
            directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password)

    def test_connect_join_failure(self):
        get_response = self._get_workgroup_param()
        self._init_filer(get_response=get_response)
        tcp_connect_return_value = TCPConnectResult(self._domain, self._ldap_port, True)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=tcp_connect_return_value)
        self._filer.execute = mock.MagicMock(side_effect=task_manager_base.TaskError(self._task_id))

        with self.assertRaises(exception.CTERAException):
            directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password)

        self._filer.network.tcp_connect.assert_called_once_with(self._ldap_service)

        self._filer.get.assert_called_once_with('/config/fileservices/cifs')

        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)
        expected_param = self._get_domain_param()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.execute.assert_called_once_with("/status/fileservices/cifs", "joinDomain", mock.ANY)
        expected_param = self._get_domain_join_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_connect_connection_error(self):
        tcp_connect_return_value = TCPConnectResult(self._domain, self._ldap_port, False)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=tcp_connect_return_value)

        with self.assertRaises(exception.CTERAConnectionError) as error:
            directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password)

        self._filer.network.tcp_connect.assert_called_once_with(self._ldap_service)
        self.assertEqual('Unable to establish connection', error.exception.message)

    def test_set_advanced_mapping(self):
        get_response = TestEdgeDirectoryService._get_advanced_mapping_object(self._domain_flat_name, 0, 0)
        self._init_filer(get_response=get_response)
        directoryservice.DirectoryService(self._filer).advanced_mapping(self._domain_flat_name, self._mapping_min, self._mapping_max)
        self._filer.get.assert_called_once_with('/config/fileservices/cifs/idMapping/map')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/idMapping/map', mock.ANY)

        expected_param = TestEdgeDirectoryService._get_advanced_mapping_object(self._domain_flat_name, self._mapping_min, self._mapping_max)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(expected_param[0], actual_param[0])

    def test_set_advanced_mapping_raise(self):
        self.patch_call("cterasdk.edge.directoryservice.DirectoryService.domains")
        get_response = self._get_advanced_mapping_object('Invalid domain name', 0, 0)
        self._init_filer(get_response=get_response)
        with self.assertRaises(exception.CTERAException) as error:
            directoryservice.DirectoryService(self._filer).advanced_mapping(self._domain_flat_name, self._mapping_min, self._mapping_max)
        self.assertEqual('Could not find domain name', error.exception.message)

    def test_domains(self):
        domain = Object()
        domain.flatName = self._domain_flat_name
        execute_response = [domain]
        self._init_filer(execute_response=execute_response)
        ret = directoryservice.DirectoryService(self._filer).domains()
        self._filer.execute.assert_called_once_with('/status/fileservices/cifs', 'enumDiscoveredDomains')
        self.assertEqual(ret[0], self._domain_flat_name)

    def test_disconnect(self):
        get_response = self._get_domain_param()
        self._init_filer(get_response=get_response)
        directoryservice.DirectoryService(self._filer).disconnect()
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_workgroup_param()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_get_connected_domain(self):
        obj = Object()
        obj.type = 'domain'
        obj.domain = self._domain
        obj.workgroup = None
        self._init_filer(get_response=obj)
        ret = directoryservice.DirectoryService(self._filer).get_connected_domain()
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._assert_equal_objects(ret, obj)

    def test_get_static_domain_controller(self):
        self._init_filer(get_response=self._dc)
        ret = directoryservice.DirectoryService(self._filer).get_static_domain_controller()
        ret = self._filer.get.assert_called_once_with('/config/fileservices/cifs/passwordServer')
        self.assertEqual(ret, self._dc)

    def test_set_static_domain_controller(self):
        self._init_filer(put_response=self._dc)
        ret = directoryservice.DirectoryService(self._filer).set_static_domain_controller(self._dc)
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/passwordServer', self._dc)
        self.assertEqual(ret, self._dc)

    def test_remove_static_domain_controller(self):
        self._init_filer()
        directoryservice.DirectoryService(self._filer).remove_static_domain_controller(self._dc)
        self._filer.put.assert_called_once_with('/config/fileservices/cifs/passwordServer', None)

    @staticmethod
    def _get_advanced_mapping_object(domain_flat_name, min_id, max_id):
        mapping = Object()
        mapping.domainFlatName = domain_flat_name
        mapping.minID = min_id
        mapping.maxID = max_id
        return [mapping]

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
