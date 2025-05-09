from unittest import mock
import munch

from cterasdk import exceptions
from cterasdk.edge import login
from tests.ut.edge import base_edge


class TestEdgeLogin(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._username = 'admin'
        self._password = 'password'
        self._version = '7.5.182.16'
        self._mock_close = self.patch_call("cterasdk.clients.clients.Client.close")

    def test_login_success(self):
        self._init_filer()
        self._init_ctera_migrate()
        login.Login(self._filer).login(self._username, self._password)
        self._filer.api.form_data.assert_called_once_with('/login', {'username': self._username, 'password': self._password})
        self._filer.migrate.login.assert_called_once()  # pylint: disable=protected-access

    def test_login_failure(self):
        error_message = "Expected Failure"
        expected_exception = exceptions.CTERAException(message=error_message)
        self._filer.api.form_data = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            login.Login(self._filer).login(self._username, self._password)
        self.assertEqual(error_message, error.exception.message)

    def test_login_required(self):
        with self.assertRaises(exceptions.NotLoggedIn) as error:
            self._filer.api.get('/config/device')
        self.assertEqual('Not logged in.', error.exception.message)

    def test_logout_success_after_login_success(self):
        self._init_filer()
        self._filer.api.get = mock.MagicMock(side_effect=[munch.Munch(dict(username=self._username)), self._version])
        self._init_ctera_migrate()
        self._filer.login(self._username, self._password)
        self._filer.logout()
        self._filer.api.form_data.assert_has_calls(
            [
                mock.call('/login', {'username': self._username, 'password': self._password}),
                mock.call('/logout', {'foo': 'bar'})
            ]
        )
        self._filer.migrate.login.assert_called_once()  # pylint: disable=protected-access
        self._mock_close.assert_called_once()

    def test_logout_failure_after_login_success(self):
        self._init_filer()
        self._filer.api.get = mock.MagicMock(side_effect=[munch.Munch(dict(username=self._username)), self._version])
        self._init_ctera_migrate()
        self._filer.login(self._username, self._password)
        self._filer.api.form_data.assert_called_once_with('/login', {'username': self._username, 'password': self._password})
        self._filer.migrate.login.assert_called_once()  # pylint: disable=protected-access
        error_message = "Expected Failure"
        self._filer.api.form_data = mock.MagicMock(side_effect=exceptions.CTERAException(message=error_message))
        with self.assertRaises(exceptions.CTERAException) as error:
            login.Login(self._filer).logout()
        self._filer.api.form_data.assert_called_once_with('/logout', {'foo': 'bar'})
        self.assertEqual(error_message, error.exception.message)
