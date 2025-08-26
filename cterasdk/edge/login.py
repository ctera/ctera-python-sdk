import logging

from ..exceptions.transport import InternalServerError
from ..exceptions.auth import AuthenticationError
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Login(BaseCommand):

    def info(self):
        """
        Get login info
        """
        return self._edge.api.get('/nosession/logininfo')

    def login(self, username, password):
        """
        Log in to CTERA Edge Filer

        :param str username: User name
        :param str password: User password
        :raises: :class:`cterasdk.exceptions.auth.AuthenticationError`
        """
        host = self._edge.host()
        try:
            self._edge.api.form_data('/login', {'username': username, 'password': password})
            logger.info("User logged in. %s", {'host': host, 'user': username})
            self._edge.ctera_migrate.login()
        except InternalServerError as e:
            logger.error("Login failed. %s", {'host': host, 'user': username})
            if e.error.response.error.msg == 'Wrong username or password':
                raise AuthenticationError() from e
            raise

    def sso(self, ticket):
        """
        Single Sign On

        :param str ticket: SSO Ticket.
        """
        logger.info("Performing Single Sign On.")
        self._edge.api.get('/ssologin', params={'ticket': ticket})
        self._edge.ctera_migrate.login()

    def logout(self):
        host = self._edge.host()
        user = self._edge.session().account.name
        self._edge.api.form_data('/logout', {'foo': 'bar'})
        logger.info("User logged out. %s", {'host': host, 'user': user})
