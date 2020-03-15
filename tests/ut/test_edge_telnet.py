from unittest import mock

from cterasdk import exception
from cterasdk.edge import telnet
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeTelnet(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._telnet_code = '8a1ab2b'

    def test_enable_telnet_success(self):
        execute_response = 'OK'
        self._init_filer(execute_response=execute_response)
        telnet.Telnet(self._filer).enable(self._telnet_code)
        self._filer.execute.assert_called_once_with('/config/device', 'startTelnetd', mock.ANY)

        expected_param = self._get_telnet_object()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

    def test_enable_telnet_already_running(self):
        execute_response = 'telnetd already running'
        self._init_filer(execute_response=execute_response)
        telnet.Telnet(self._filer).enable(self._telnet_code)
        self._filer.execute.assert_called_once_with('/config/device', 'startTelnetd', mock.ANY)

        expected_param = self._get_telnet_object()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

    def test_enable_telnet_raise(self):
        execute_response = 'Expected Failure'
        self._init_filer(execute_response=execute_response)
        with self.assertRaises(exception.CTERAException) as error:
            telnet.Telnet(self._filer).enable(self._telnet_code)

        self._filer.execute.assert_called_once_with('/config/device', 'startTelnetd', mock.ANY)
        expected_param = self._get_telnet_object()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual('Failed enabling telnet access', error.exception.message)

    def test_disable_telnet(self):
        self._init_filer()
        telnet.Telnet(self._filer).disable()
        self._filer.execute.assert_called_once_with('/config/device', 'stopTelnetd')

    def _get_telnet_object(self):
        telnet_param = Object()
        telnet_param.code = self._telnet_code
        return telnet_param
