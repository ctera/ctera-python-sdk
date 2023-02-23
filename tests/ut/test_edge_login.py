from unittest import mock

from cterasdk import exception
from cterasdk.edge import login
from tests.ut import base_edge


class TestEdgeLogin(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._username = 'admin'
        self._password = 'password'

    def test_login_success(self):
        self._init_filer()
        self._init_ctera_migrate()
        login.Login(self._filer).login(self._username, self._password)
        self._filer.form_data.assert_called_once_with('/login', {'username': self._username, 'password': self._password})
        self._filer._ctera_migrate.login.assert_called_once_with('/migration/rest/v1/auth/user')  # pylint: disable=protected-access

    def test_login_failure(self):
        error_message = "Expected Failure"
        expected_exception = exception.CTERAException(message=error_message)
        self._filer.form_data = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            login.Login(self._filer).login(self._username, self._password)
        self.assertEqual(error_message, error.exception.message)

    def test_login_required(self):
        with self.assertRaises(exception.CTERAException) as error:
            self._filer.get('/config/device')
        self.assertEqual('Not logged in', error.exception.message)

    def test_logout_success_after_login_success(self):
        self._init_filer()
        self._init_ctera_migrate()
        login.Login(self._filer).login(self._username, self._password)
        login.Login(self._filer).logout()
        self._filer.form_data.assert_has_calls(
            [
                mock.call('/login', {'username': self._username, 'password': self._password}),
                mock.call('/logout', {'foo': 'bar'})
            ]
        )
        self._filer._ctera_migrate.login.assert_called_once_with('/migration/rest/v1/auth/user')  # pylint: disable=protected-access

    def test_logout_failure_after_login_success(self):
        self._init_filer()
        self._init_ctera_migrate()
        login.Login(self._filer).login(self._username, self._password)
        self._filer.form_data.assert_called_once_with('/login', {'username': self._username, 'password': self._password})
        self._filer._ctera_migrate.login.assert_called_once_with('/migration/rest/v1/auth/user')  # pylint: disable=protected-access
        error_message = "Expected Failure"
        expected_exception = exception.CTERAException(message=error_message)
        self._filer.form_data = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            login.Login(self._filer).logout()
        self._filer.form_data.assert_called_once_with('/logout', {'foo': 'bar'})
        self.assertEqual(error_message, error.exception.message)
