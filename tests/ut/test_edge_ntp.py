from unittest import mock

from cterasdk.edge import ntp
from cterasdk.edge.enum import Mode
from tests.ut import base_edge


class TestEdgeNTP(base_edge.BaseEdgeTest):

    def test_get_configuration(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = ntp.NTP(self._filer).get_configuration()
        self._filer.api.get.assert_called_once_with('/config/time')
        self.assertEqual(ret, get_response)

    def test_enable_ntp(self):
        self._init_filer()
        ntp.NTP(self._filer).enable()
        self._filer.api.put.assert_called_once_with('/config/time/NTPMode', Mode.Enabled)

    def test_disable_ntp(self):
        self._init_filer()
        ntp.NTP(self._filer).disable()
        self._filer.api.put.assert_called_once_with('/config/time/NTPMode', Mode.Disabled)

    def test_enable_ntp_with_servers(self):
        servers = [str(i) + '.pool.ntp.org' for i in range(0, 3)]
        self._init_filer()
        ntp.NTP(self._filer).enable(servers)
        self._filer.api.put.assert_has_calls(
            [
                mock.call('/config/time/NTPMode', Mode.Enabled),
                mock.call('/config/time/NTPServer', servers)
            ]
        )
