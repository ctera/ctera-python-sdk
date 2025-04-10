"""Unit tests for edge NTP configuration"""
from unittest import mock

from cterasdk.edge import ntp
from cterasdk.edge.enum import Mode
from tests.ut.edge import base_edge


class TestEdgeNTP(base_edge.BaseEdgeTest):
    """Edge NTP configuration test cases"""

    def setUp(self):
        """Setup for all test cases"""
        super().setUp()
        self.ntp_servers = ['0.pool.ntp.org', '1.pool.ntp.org', '2.pool.ntp.org']

    def test_get_configuration(self):
        """Test getting NTP configuration"""
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = ntp.NTP(self._filer).get_configuration()
        self._filer.api.get.assert_called_once_with('/config/time')
        self.assertEqual(ret, get_response)

    def test_get_servers(self):
        """Test getting NTP servers"""
        self._init_filer(get_response=self.ntp_servers)
        ret = ntp.NTP(self._filer).servers
        self._filer.api.get.assert_called_once_with('/config/time/NTPServer')
        self.assertEqual(ret, self.ntp_servers)

    def test_enable_ntp(self):
        """Test enabling NTP without servers"""
        self._init_filer()
        ntp.NTP(self._filer).enable()
        self._filer.api.put.assert_called_once_with('/config/time/NTPMode', Mode.Enabled)

    def test_disable_ntp(self):
        """Test disabling NTP"""
        self._init_filer()
        ntp.NTP(self._filer).disable()
        self._filer.api.put.assert_called_once_with('/config/time/NTPMode', Mode.Disabled)

    def test_enable_ntp_with_servers(self):
        """Test enabling NTP with custom servers"""
        self._init_filer()
        ntp.NTP(self._filer).enable(self.ntp_servers)
        expected_calls = [
            mock.call('/config/time/NTPMode', Mode.Enabled),
            mock.call('/config/time/NTPServer', self.ntp_servers)
        ]
        self._filer.api.put.assert_has_calls(expected_calls)
        self.assertEqual(self._filer.api.put.call_count, 2)
