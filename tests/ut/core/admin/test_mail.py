from unittest import mock

from cterasdk.core import mail
from cterasdk.common import Object
from tests.ut.core.admin import base_admin


class TestCoreMail(base_admin.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._host = 'host'
        self._port = 587
        self._sender = 'support@ctera.com'
        self._user = 'user'
        self._password = 'password'

    def test_is_enabled(self):
        for status in [True, False]:
            self._init_global_admin(get_response=status)
            ret = mail.Mail(self._global_admin).is_enabled()
            self._global_admin.api.get.assert_called_once_with('/settings/enableEmailSending')
            self.assertEqual(ret, status)

    def test_enable(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response, get_response=self._default_settings_object())
        ret = mail.Mail(self._global_admin).enable(self._host, self._port, self._sender, self._user, self._password, True)
        self._global_admin.api.get.assert_called_once_with('/settings')
        self._global_admin.api.put.assert_called_once_with('/settings', mock.ANY)
        expected_param = self._create_settings_object()
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_modify(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response, get_response=self._default_settings_object())
        ret = mail.Mail(self._global_admin).modify(self._host, self._port, self._sender, self._user, self._password, True)
        self._global_admin.api.put.assert_called_once_with('/settings', mock.ANY)
        expected_param = self._create_settings_object()
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_disable(self):
        self._init_global_admin()
        mail.Mail(self._global_admin).disable()
        self._global_admin.api.put.assert_called_once_with('/settings/enableEmailSending', False)

    def _default_settings_object(self):
        return self._create_settings_object('default', 587, 'no-reply@acme.com', 'user', 'pass', False)

    def _create_settings_object(self, host=None, port=None, sender=None, user=None, password=None, use_tls=None):
        settings = Object()
        settings.enableEmailSending = True
        settings.smtpSettings = Object()
        settings.smtpSettings.smtpHost = host if host else self._host
        settings.smtpSettings.smtpPort = port if port else self._port
        settings.defaultPortalSettings = Object()
        settings.defaultPortalSettings.mailSettings = Object()
        settings.defaultPortalSettings.mailSettings.sender = sender if sender else self._sender
        settings.smtpSettings.user = user if user else self._user
        settings.smtpSettings.password = password if password else self._password
        settings.smtpSettings.enableTls = use_tls if use_tls else True
        return settings
