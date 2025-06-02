import munch
from unittest import mock
from http import HTTPStatus
from cterasdk.common import Object
from cterasdk import exceptions
from tests.ut.aio import base_core


class TestAsyncCoreLogin(base_core.BaseAsyncCoreTest):

    _tenant = 'ctera'
    _username = 'username'
    _password = 'password'
    _version = '7.5.182.16'

    def setUp(self):
        super().setUp()
        self._tenant = TestAsyncCoreLogin._tenant
        self._username = TestAsyncCoreLogin._username
        self._password = TestAsyncCoreLogin._password
        self._version = TestAsyncCoreLogin._version

    async def test_login_success(self):
        self._init_global_admin()
        self._global_admin.v1.api.get = mock.AsyncMock(side_effect=TestAsyncCoreLogin._obtain_session_info)
        await self._global_admin.login(self._username, self._password)
        self._global_admin.v1.api.form_data.assert_called_once_with('/login', {'j_username': self._username, 'j_password': self._password})

    async def test_login_failure(self):
        self._init_global_admin()
        self._global_admin.v1.api.form_data = mock.AsyncMock(side_effect=exceptions.HTTPError(
            HTTPStatus.FORBIDDEN,
            munch.Munch(
                dict(request=munch.Munch(
                    dict(url='/xyz')
                ))
            )
        ))
        with self.assertRaises(exceptions.CTERAException):
            await self._global_admin.login(self._username, self._password)

    async def test_logout_success_after_login(self):
        self._init_global_admin()
        self._global_admin.v1.api.get = mock.AsyncMock(side_effect=TestAsyncCoreLogin._obtain_session_info)
        await self._global_admin.login(self._username, self._password)
        await self._global_admin.logout()
        self._global_admin.v1.api.form_data.assert_has_calls(
            [
                mock.call('/login', {'j_username': self._username, 'j_password': self._password}),
                mock.call('/logout', {})
            ]
        )

    @staticmethod
    def _obtain_session_info(path):
        if path == '/currentPortal':
            return TestAsyncCoreLogin._tenant
        if path == '/version':
            return TestAsyncCoreLogin._version
        if path == '/currentSession':
            current_session = Object()
            current_session.username = TestAsyncCoreLogin._username
            current_session.role = TestAsyncCoreLogin._password
            current_session.domain = None
            return current_session
        return ''
