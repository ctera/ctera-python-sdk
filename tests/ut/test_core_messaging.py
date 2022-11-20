from unittest import mock

from cterasdk.common import Object
from cterasdk.core import messaging
from tests.ut import base_core


class TestCoreMessaging(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._servers = ["server1", "server2", "server3"]
        self._messaging = Object()

        self._messaging.globalStatus = Object()
        self._messaging.globalStatus._class = "GlobalMessagingStatus"  # pylint: disable=protected-access
        self._messaging.globalStatus.status = "Active"
        self._messaging.globalStatus.canAddServers = True
        self._messaging.globalStatus.cantAddServersReason = ""
        self._messaging.globalStatus.validServerNumber = [1, 3]

        self._messaging.availableNodes = []
        self._messaging.currentNodes = []
        for server in self._servers:
            _node = Object()
            _node._class = "MessagingServerCandidate"  # pylint: disable=protected-access
            _node.canAssignAsMessaging = Object()
            _node.canAssignAsMessaging.allowed = True
            _node.server = Object()
            _node.server.name = server
            self._messaging.availableNodes.append(_node)

    def test_status(self):
        self._init_global_admin(get_response=self._messaging.globalStatus)
        ret = messaging.Messaging(self._global_admin).get_status()
        self._global_admin.get.assert_called_once_with('/microservices/messaging/globalStatus')
        self.assertEqual(ret, self._messaging.globalStatus)

    def test_is_active(self):
        self._init_global_admin(get_response=self._messaging.globalStatus)
        messaging.Messaging(self._global_admin).is_active()
        self._global_admin.get.assert_called_once_with('/microservices/messaging/globalStatus')

    def test_add_server(self):
        self._init_global_admin(get_response=self._messaging)
        messaging.Messaging(self._global_admin).add(self._servers)
        self._global_admin.get.assert_called_once_with('/microservices/messaging')
        self._global_admin.put.assert_called_once_with('microservices/messaging/currentNodes', mock.ANY)
        expected_param = self._get_current_node_objects()
        actual_param = self._global_admin.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def _get_current_node_objects(self):
        nodes = []
        for node in self._messaging.availableNodes:
            current_node_object = Object()
            current_node_object._class = "CurrentMessagingNode"  # pylint: disable=protected-access
            current_node_object.server = node.server
            current_node_object.serverStatus = Object()
            current_node_object.serverStatus.status = "Running"
            current_node_object.serverStatus._class = "MessagingServerStatus"  # pylint: disable=protected-access
            nodes.append(current_node_object)
        return nodes
