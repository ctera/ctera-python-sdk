from unittest import mock

from cterasdk.common import Object
from cterasdk.core import login
from tests.ut.core.admin import base_admin


class TestCoreLogin(base_admin.BaseCoreTest):

    _tenant = 'acme'
    _username = 'admin'
    _password = 'password'
    _role = 'ReadWriteAdmin'
    _version = '7.5.182.16'

    def setUp(self):
        super().setUp()
        self._tenant = TestCoreLogin._tenant
        self._username = TestCoreLogin._username
        self._password = TestCoreLogin._password
        self._role = TestCoreLogin._role

    @staticmethod
    def _obtain_session_info(path):
        if path == '/currentPortal':
            return TestCoreLogin._tenant
        if path == '/version':
            return TestCoreLogin._version
        if path == '/currentSession':
            current_session = Object()
            current_session.username = TestCoreLogin._username
            current_session.role = TestCoreLogin._password
            current_session.domain = None
            return current_session
        return ''

    def test_login_success(self):
        self._init_global_admin()
        self._global_admin.api.get = mock.MagicMock(side_effect=TestCoreLogin._obtain_session_info)
        login.Login(self._global_admin).login(self._username, self._password)
        self._global_admin.api.form_data.assert_called_once_with('/login', {'j_username': self._username, 'j_password': self._password})

    def test_logout_success_after_login(self):
        self._init_global_admin()
        self._global_admin.api.get = mock.MagicMock(side_effect=TestCoreLogin._obtain_session_info)
        self._global_admin.login(self._username, self._password)
        self._global_admin.logout()
        self._global_admin.api.form_data.assert_has_calls(
            [
                mock.call('/login', {'j_username': self._username, 'j_password': self._password}),
                mock.call('/logout', {})
            ]
        )
