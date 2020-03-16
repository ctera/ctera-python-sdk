from unittest import mock

from cterasdk import exception
from cterasdk.edge import directoryservice
from cterasdk.common import Object
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

    def test_connect(self):
        get_response = self._get_workgroup_param()
        self._init_filer(get_response=get_response)
        tcp_connect_return_value = True
        self._filer.network.tcp_connect = mock.MagicMock(return_value=tcp_connect_return_value)

        directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password)

        self._filer.network.tcp_connect.assert_called_once_with(address=self._domain, port=389)
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_domain_param()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

        self._filer.execute.assert_called_once_with("/status/fileservices/cifs", "joinDomain", mock.ANY)
        expected_param = self._get_domain_join_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

    def test_connect_with_ou_path(self):
        ou_path = "ou=North America,DC=ctera,DC=local"
        get_response = self._get_workgroup_param()
        self._init_filer(get_response=get_response)
        tcp_connect_return_value = True
        self._filer.network.tcp_connect = mock.MagicMock(return_value=tcp_connect_return_value)

        directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password, ou_path)

        self._filer.network.tcp_connect.assert_called_once_with(address=self._domain, port=389)
        self._filer.get.assert_called_once_with('/config/fileservices/cifs')
        self._filer.put.assert_called_once_with('/config/fileservices/cifs', mock.ANY)

        expected_param = self._get_domain_param()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

        self._filer.execute.assert_called_once_with("/status/fileservices/cifs", "joinDomain", mock.ANY)
        expected_param = self._get_domain_join_param(ou_path)
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

    def test_connect_raise(self):
        get_response = self._get_workgroup_param()
        self._init_filer(get_response=get_response)

        expected_exception = exception.CTERAException()
        self._filer.execute = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException):
            directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password)

    def test_connect_connection_error(self):
        tcp_connect_return_value = False
        self._filer.network.tcp_connect = mock.MagicMock(return_value=tcp_connect_return_value)

        with self.assertRaises(exception.CTERAConnectionError) as error:
            directoryservice.DirectoryService(self._filer).connect(self._domain, self._username, self._password)

        self._filer.network.tcp_connect.assert_called_once_with(address=self._domain, port=389)
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
        self._assert_equal_objects(expected_param, actual_param)

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
