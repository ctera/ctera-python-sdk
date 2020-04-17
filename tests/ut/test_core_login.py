from unittest import mock

from cterasdk.common import Object
from cterasdk.core import login
from tests.ut import base_core


class TestCoreLogin(base_core.BaseCoreTest):

    _tenant = 'acme'
    _username = 'admin'
    _password = 'password'
    _role = 'ReadWriteAdmin'

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
        if path == '/currentSession':
            current_session = Object()
            current_session.username = TestCoreLogin._username
            current_session.role = TestCoreLogin._password
            return current_session
        return ''

    def test_login_success(self):
        self._init_global_admin()
        self._global_admin.get = mock.MagicMock(side_effect=TestCoreLogin._obtain_session_info)
        login.Login(self._global_admin).login(self._username, self._password)
        self._global_admin.form_data.assert_called_once_with('/login', {'j_username': self._username, 'j_password': self._password})

    def test_logout_success(self):
        self._init_global_admin()
        login.Login(self._global_admin).logout()
        self._global_admin.form_data.assert_called_once_with('/logout', {})
