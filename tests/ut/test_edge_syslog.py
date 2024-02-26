from unittest import mock

from cterasdk import exception
from cterasdk.edge import syslog
from cterasdk.edge.enum import IPProtocol, Severity, Mode
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeSyslog(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._syslog_server = 'syslog.ctera.local'
        self._custom_syslog_server = 'custom.syslog.ctera.local'
        self._default_syslog_port = 514
        self._custom_syslog_port = 614
        self._udp = IPProtocol.UDP
        self._tcp = IPProtocol.TCP
        self._default_min_severity = Severity.INFO
        self._min_severity = Severity.ERROR

    def test_get_configuration(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = syslog.Syslog(self._filer).get_configuration()
        self._filer.get.assert_called_once_with('/config/logging/syslog')
        self._assert_equal_objects(ret, get_response)

    def test_enable_syslog_default_params(self):
        self._init_filer()
        syslog.Syslog(self._filer).enable(self._syslog_server)
        self._filer.put.assert_called_once_with('/config/logging/syslog', mock.ANY)

        expected_param = self._get_syslog_object()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_syslog_custom_port(self):
        self._init_filer()
        syslog.Syslog(self._filer).enable(self._syslog_server, self._custom_syslog_port)
        self._filer.put.assert_called_once_with('/config/logging/syslog', mock.ANY)

        expected_param = self._get_syslog_object(port=self._custom_syslog_port)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_syslog_custom_port_use_tcp_default_severity(self):
        self._init_filer()
        syslog.Syslog(self._filer).enable(self._syslog_server, self._custom_syslog_port, self._tcp)
        self._filer.put.assert_called_once_with('/config/logging/syslog', mock.ANY)

        expected_param = self._get_syslog_object(port=self._custom_syslog_port, protocol=self._tcp)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_syslog_custom_port_use_tcp_severity_error(self):
        self._init_filer()
        syslog.Syslog(self._filer).enable(self._syslog_server, self._custom_syslog_port, self._tcp, self._min_severity)
        self._filer.put.assert_called_once_with('/config/logging/syslog', mock.ANY)

        expected_param = self._get_syslog_object(port=self._custom_syslog_port, protocol=self._tcp, min_severity=self._min_severity)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_disable_syslog(self):
        self._init_filer()
        syslog.Syslog(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/logging/syslog/mode', Mode.Disabled)

    def test_modify_success(self):
        self._init_filer(get_response=self._get_syslog_object())
        syslog.Syslog(self._filer).modify(self._custom_syslog_server, self._custom_syslog_port, self._tcp, self._min_severity)
        self._filer.get.assert_called_once_with('/config/logging/syslog')
        self._filer.put.assert_called_once_with('/config/logging/syslog', mock.ANY)
        expected_param = self._get_syslog_object(self._custom_syslog_server, self._custom_syslog_port, self._tcp, self._min_severity)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_raise(self):
        param = Object()
        param.mode = Mode.Disabled
        self._init_filer(get_response=param)
        with self.assertRaises(exceptions.CTERAException) as error:
            syslog.Syslog(self._filer).modify()
        self.assertEqual('Syslog configuration cannot be modified when disabled', error.exception.message)

    def _get_syslog_object(self, server=None, port=None, protocol=None, min_severity=None):
        syslog_param = Object()
        syslog_param.mode = Mode.Enabled
        syslog_param.server = self._syslog_server if server is None else server
        syslog_param.port = self._default_syslog_port if port is None else port
        syslog_param.proto = self._udp if protocol is None else protocol
        syslog_param.minSeverity = self._default_min_severity if min_severity is None else min_severity
        return syslog_param
