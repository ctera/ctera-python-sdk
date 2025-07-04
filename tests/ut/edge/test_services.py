from unittest import mock

from cterasdk import exceptions
from cterasdk.lib import task_manager_base
from cterasdk.edge import services
from cterasdk.edge.enum import ServicesConnectionState
from cterasdk.edge.types import TCPService, TCPConnectResult
from cterasdk.common import Object
from tests.ut.edge import base_edge


class TestEdgeServices(base_edge.BaseEdgeTest):  # pylint: disable=too-many-instance-attributes

    _background_task_id = 1000

    def setUp(self):
        super().setUp()
        self._server = 'test.ctera.me'
        self._user = 'user'
        self._password = 'password'
        self._code = '189d0-b01a2d'
        self._ip_address = '8.8.8.8'
        self._user_display_name = 'Alice Wonderland'
        self._portal_version = '6.0.744'
        self._server_address = 'cti.ctera.com'
        self._last_connnected_at = '2020-04-05T10:55:00'

        self._cttp_port = 995
        self._cttp_service = TCPService(self._server, self._cttp_port)
        self._tracker_mock = self.patch_call("cterasdk.edge.services.track")
        self._network_proxy_status_mock = self.patch_call("cterasdk.edge.network.Proxy.is_enabled")
        self._network_proxy_status_mock.return_value = False

    def test_get_services_status(self):
        self._init_filer(get_response=self._get_services_status_response())
        ret = services.Services(self._filer).get_status()
        self._filer.api.get.assert_called_once_with('/status/services')
        expected_return_value = self._get_services_connection_status()
        self._assert_equal_objects(ret, expected_return_value)

    def test_activate_default_args_success(self):
        self._init_filer()
        self._filer.api.execute = mock.MagicMock(side_effect=TestEdgeServices._mock_execute_connect_ok)
        self._filer.tasks.wait = mock.MagicMock()
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._server, self._cttp_port, True))
        services.Services(self._filer).activate(self._server, self._user, self._code)

        self._filer.network.tcp_connect.assert_called_once_with(self._cttp_service)
        self._filer.api.execute.assert_called_once_with('/status/services', 'attachAndSave', mock.ANY)
        self._filer.tasks.wait.assert_called_once_with(TestEdgeServices._background_task_id)
        expected_param = self._get_attach_and_save_param(False, use_activation_code=True)
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self._tracker_mock.assert_called_once_with(
            self._filer,
            '/status/services/CTERAPortal/connectionState',
            [ServicesConnectionState.Connected],
            [ServicesConnectionState.ResolvingServers, ServicesConnectionState.Connecting,
             ServicesConnectionState.Attaching, ServicesConnectionState.Authenticating],
            [],
            [ServicesConnectionState.Disconnected],
            20,
            1)

    def test_connect_default_args_success(self):
        self._init_filer()
        self._filer.api.execute = mock.MagicMock(side_effect=TestEdgeServices._mock_execute_connect_ok)
        self._filer.tasks.wait = mock.MagicMock()
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._server, self._cttp_port, True))

        services.Services(self._filer).connect(self._server, self._user, self._password)

        self._filer.network.tcp_connect.assert_called_once_with(self._cttp_service)
        self._filer.api.execute.assert_has_calls(
            [
                mock.call('/status/services', 'isWebSsoEnabled', mock.ANY),
                mock.call('/status/services', 'attachAndSave', mock.ANY)
            ]
        )
        self._filer.tasks.wait.assert_called_once_with(TestEdgeServices._background_task_id)
        expected_param = self._get_is_web_sso_param(trust_certificate=False)
        actual_param = self._filer.api.execute.call_args_list[0][0][2]  # Access isWebSSOEnabled call param

        self._assert_equal_objects(actual_param, expected_param)
        expected_param = self._get_attach_and_save_param(False, use_activation_code=False)
        actual_param = self._filer.api.execute.call_args_list[1][0][2]  # Access attachAndSave call param
        self._assert_equal_objects(actual_param, expected_param)
        self._tracker_mock.assert_called_once_with(
            self._filer,
            '/status/services/CTERAPortal/connectionState',
            [ServicesConnectionState.Connected],
            [ServicesConnectionState.ResolvingServers, ServicesConnectionState.Connecting,
             ServicesConnectionState.Attaching, ServicesConnectionState.Authenticating],
            [],
            [ServicesConnectionState.Disconnected],
            20,
            1)

    def test_connect_tcp_connect_error(self):
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._server, self._cttp_port, False))
        with self.assertRaises(ConnectionError) as error:
            services.Services(self._filer).connect(self._server, self._user, self._password)
        self._filer.network.tcp_connect.assert_called_once_with(self._cttp_service)
        self.assertEqual(f'Unable to establish CTTP connection {self._server}:{self._cttp_port}', str(error.exception))

    def test_connect_require_sso_failure(self):
        self._init_filer(execute_response=TestEdgeServices._check_web_sso_require_sso())
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._server, self._cttp_port, True))

        with self.assertRaises(exceptions.CTERAException) as error:
            services.Services(self._filer).connect(self._server, self._user, self._password)

        self._filer.network.tcp_connect.assert_called_once_with(self._cttp_service)
        self._filer.api.execute.assert_called_once_with('/status/services', 'isWebSsoEnabled', mock.ANY)
        expected_param = self._get_is_web_sso_param(False)
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual('Connection failed. You must activate this Edge Filer using an activation code.', str(error.exception))

    def test_connect_default_args_task_failure(self):
        self._init_filer()
        self._filer.api.execute = mock.MagicMock(side_effect=TestEdgeServices._mock_execute_connect_ok)
        task_error_side_effect = TestEdgeServices._get_task_error()
        self._filer.tasks.wait = mock.MagicMock(side_effect=task_error_side_effect)
        self._filer.network.tcp_connect = mock.MagicMock(return_value=TCPConnectResult(self._server, self._cttp_port, True))

        with self.assertRaises(exceptions.CTERAException) as error:
            services.Services(self._filer).connect(self._server, self._user, self._password)

        self._filer.network.tcp_connect.assert_called_once_with(self._cttp_service)
        self._filer.api.execute.assert_has_calls(
            [
                mock.call('/status/services', 'isWebSsoEnabled', mock.ANY),
                mock.call('/status/services', 'attachAndSave', mock.ANY)
            ]
        )
        self._filer.tasks.wait.assert_called_once_with(TestEdgeServices._background_task_id)

        expected_param = self._get_is_web_sso_param(trust_certificate=False)
        actual_param = self._filer.api.execute.call_args_list[0][0][2]  # Access isWebSSOEnabled call param
        self._assert_equal_objects(actual_param, expected_param)

        expected_param = self._get_attach_and_save_param(False, use_activation_code=False)
        actual_param = self._filer.api.execute.call_args_list[1][0][2]  # Access attachAndSave call param
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(f'Connection failed. Reason: {task_error_side_effect.task.description}', str(error.exception))

    def test_reconnect(self):
        self._init_filer()
        services.Services(self._filer).reconnect()
        self._filer.api.execute.assert_called_once_with('/status/services', 'reconnect', None)

    def test_disconnect(self):
        self._init_filer()
        services.Services(self._filer).disconnect()
        self._filer.api.put.assert_called_once_with('/config/services', None)

    def test_sso_enabled(self):
        get_response = True
        self._init_filer(get_response=get_response)
        ret = services.Services(self._filer).sso_enabled()
        self._filer.api.get.assert_called_once_with('/config/gui/adminRemoteAccessSSO')
        self.assertEqual(ret, get_response)

    def test_enable_sso(self):
        self._init_filer()
        services.Services(self._filer).enable_sso()
        self._filer.api.put.assert_called_once_with('/config/gui/adminRemoteAccessSSO', True)

    def test_disable_sso(self):
        self._init_filer()
        services.Services(self._filer).disable_sso()
        self._filer.api.put.assert_called_once_with('/config/gui/adminRemoteAccessSSO', False)

    def _get_services_connection_status(self):
        param = Object()
        param.connection = Object()
        param.connected = True
        param.ipaddr = self._ip_address
        param.user = self._user_display_name
        param.server_version = self._portal_version
        param.server_address = self._server_address
        param.last_connected_at = self._last_connnected_at
        return param

    def _get_services_status_response(self):
        status = Object()
        status.CTERAPortal = Object()
        status.CTERAPortal.connectionState = ServicesConnectionState.Connected
        status.CTERAPortal.connectedAddress = self._ip_address
        status.userDisplayName = self._user_display_name
        status.portalVersion = self._portal_version
        server = Object()
        server.name = self._server_address
        status.CTERAPortal.serverList = [server]
        status.CTERAPortal.establishedTime = self._last_connnected_at
        return status

    @staticmethod
    def _get_task_error():
        error = task_manager_base.TaskError(TestEdgeServices._background_task_id)
        error.task = Object()
        error.task.description = 'Reason for Failure'
        return error

    def _get_attach_and_save_param(self, trust_certificate, use_activation_code=False):
        param = Object()
        param.server = self._server
        param.user = self._user
        if use_activation_code:
            param.activationCode = self._code
        else:
            param.password = self._password
        param.trustCertificate = trust_certificate
        return param

    def _get_is_web_sso_param(self, trust_certificate):
        param = Object()
        param.server = self._server
        param.trustCertificate = trust_certificate
        return param

    @staticmethod
    def _mock_execute_connect_ok(path, name, param):
        # pylint: disable=unused-argument
        if name == 'isWebSsoEnabled':
            return TestEdgeServices._check_web_sso_connect_ok()
        return TestEdgeServices._attach_and_save_response()

    @staticmethod
    def _attach_and_save_response():
        param = Object()
        param.id = TestEdgeServices._background_task_id
        return param

    @staticmethod
    def _check_web_sso_require_sso():
        param = Object()
        param.result = Object()
        param.result.hasWebSSO = True
        return param

    @staticmethod
    def _check_web_sso_connect_ok():
        param = Object()
        param.result = Object()
        param.result.hasWebSSO = False
        param.rc = 'connectOK'
        return param
