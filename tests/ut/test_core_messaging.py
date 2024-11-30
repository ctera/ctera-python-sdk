import warnings
from cterasdk.common import Object
from tests.ut import base_core

# Suppress the RuntimeWarning about TestResult
warnings.filterwarnings(
    'ignore',
    category=RuntimeWarning,
    message='TestResult has no addDuration method'
)


class TestCoreMessaging(base_core.BaseCoreTest):
    def setUp(self):
        super().setUp()
        self._servers = ['server1', 'server3', 'server2']

    def test_is_active(self):
        """Test messaging service active status check"""
        response = Object()
        response.status = 'Active'
        self._init_global_admin(get_response=response)
        ret = self._global_admin.messaging.is_active()
        self._global_admin.api.get.assert_called_once_with('/microservices/messaging/globalStatus')
        self.assertTrue(ret)

    def test_get_status(self):
        """Test getting messaging service global status"""
        get_response = Object()
        get_response.status = 'Active'
        self._init_global_admin(get_response=get_response)
        ret = self._global_admin.messaging.get_status()
        self._global_admin.api.get.assert_called_once_with('/microservices/messaging/globalStatus')
        self.assertEqual(ret, get_response)

    def test_get_servers_status(self):
        """Test getting messaging servers status"""
        server1 = Object()
        server1.server = Object()
        server1.server.name = 'server1'
        server1.serverStatus = Object()
        server1.serverStatus.status = 'Running'
        get_response = Object()
        get_response.currentNodes = [server1]
        self._init_global_admin(get_response=get_response)
        ret = self._global_admin.messaging.get_servers_status()
        self._global_admin.api.get.assert_called_once_with('/microservices/messaging')
        expected = {'server1: "Running"'}
        self.assertEqual(ret, expected)

    def test_add_servers_success(self):
        """Test adding servers successfully"""
        get_response = Object()
        get_response.globalStatus = Object()
        get_response.globalStatus.canAddServers = True
        get_response.globalStatus.validServerNumber = [1, 3]
        node1 = Object()
        node1.server = Object()
        node1.server.name = 'server1'
        node1.canAssignAsMessaging = Object()
        node1.canAssignAsMessaging.allowed = True
        get_response.availableNodes = [node1]
        put_response = Object()
        self._init_global_admin(get_response=get_response, put_response=put_response)
        ret = self._global_admin.messaging.add(['server1'])
        self._global_admin.api.get.assert_called_once_with('/microservices/messaging')
        self._global_admin.api.put.assert_called_once()
        self.assertEqual(ret, put_response)

    def test_add_servers_not_allowed(self):
        """Test adding servers when not allowed"""
        get_response = Object()
        get_response.globalStatus = Object()
        get_response.globalStatus.canAddServers = False
        get_response.globalStatus.cantAddServersReason = "Cluster already exists"
        self._init_global_admin(get_response=get_response)
        ret = self._global_admin.messaging.add(['server1'])
        self._global_admin.api.get.assert_called_once_with('/microservices/messaging')
        self._global_admin.api.put.assert_not_called()
        self.assertIsNone(ret)

    def test_add_servers_invalid_number(self):
        """Test adding invalid number of servers"""
        get_response = Object()
        get_response.globalStatus = Object()
        get_response.globalStatus.canAddServers = True
        get_response.globalStatus.validServerNumber = [1, 3]
        node1 = Object()
        node1.server = Object()
        node1.server.name = 'server1'
        node1.canAssignAsMessaging = Object()
        node1.canAssignAsMessaging.allowed = False
        get_response.availableNodes = [node1]
        self._init_global_admin(get_response=get_response)
        ret = self._global_admin.messaging.add(['server1', 'server2'])
        self._global_admin.api.get.assert_called_once_with('/microservices/messaging')
        self.assertIsNone(ret)
