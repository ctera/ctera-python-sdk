from unittest import mock

from cterasdk.edge import mail
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeMailServer(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._smtp_server = 'smtp_server'
        self._default_port = 25
        self._custom_port = 486
        self._username = 'admin'
        self._password = 'password'
        self._use_tls = True

    def test_enable_mail_server_default_port_no_auth_no_tls(self):
        get_response = self._get_default_mail_server_config()
        self._init_filer(get_response=get_response)
        mail.Mail(self._filer).enable(self._smtp_server)
        self._filer.get.assert_called_once_with('/config/logging/alert')
        self._filer.put.assert_called_once_with('/config/logging/alert', mock.ANY)

        expected_param = self._get_mail_server_config()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

    def test_enable_mail_server_custom_port_no_auth_with_tls(self):
        get_response = self._get_default_mail_server_config()
        self._init_filer(get_response=get_response)
        mail.Mail(self._filer).enable(self._smtp_server, self._custom_port)
        self._filer.get.assert_called_once_with('/config/logging/alert')
        self._filer.put.assert_called_once_with('/config/logging/alert', mock.ANY)

        expected_param = self._get_mail_server_config(self._custom_port)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

    def test_enable_mail_server_default_port_with_auth_with_tls(self):
        get_response = self._get_default_mail_server_config()
        self._init_filer(get_response=get_response)
        mail.Mail(self._filer).enable(self._smtp_server, self._default_port, self._username, self._password, self._use_tls)
        self._filer.get.assert_called_once_with('/config/logging/alert')
        self._filer.put.assert_called_once_with('/config/logging/alert', mock.ANY)

        expected_param = self._get_mail_server_config(self._default_port, self._username, self._password, self._use_tls)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

    def _get_default_mail_server_config(self):
        mail_param = Object()
        mail_param.port = self._default_port
        mail_param.useTLS = self._use_tls
        return mail_param

    def _get_mail_server_config(self, port=25, username=None, password=None, use_tls=True):
        mail_param = Object()
        mail_param.useCustomServer = True
        mail_param.SMTPServer = self._smtp_server
        mail_param.port = port

        if username is not None and password is not None:
            mail_param.useAuth = True
            mail_param.auth = Object()
            mail_param.auth.username = username
            mail_param.auth.password = password

        mail_param.useTLS = use_tls
        return mail_param
