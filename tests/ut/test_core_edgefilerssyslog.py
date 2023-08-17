from cterasdk.core import edgefilerssyslog
from cterasdk.core.enum import IPProtocol
from tests.ut import base_core


class TestCoreEdgeFilersSyslog(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._classname = 'SyslogServerConfig'  # pylint: disable=protected-access
        self._address = 'syslog-server-address'
        self._port = 514
        self._protocol = IPProtocol.UDP
        self._messagesLagThreshold = 100
        self._id = 12345

    def test_get_server(self):
        self._init_global_admin()
        edgefilerssyslog.EdgeFilersSyslog(self._global_admin).list_servers()
        self._global_admin.get.assert_called_once_with('/microservices/syslog/status/servers')
