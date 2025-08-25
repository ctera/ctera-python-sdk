import logging

from .base_command import BaseCommand
from ..exceptions.transport import Forbidden
from ..exceptions.session import SessionExpired
from ..exceptions.auth import AuthenticationError


logger = logging.getLogger('cterasdk.core')


class Login(BaseCommand):
    """
    Portal Login APIs
    """

    def login(self, username, password):
        """
        Log in to CTERA Portal

        :param str username: User name
        :param str password: User password
        :raises: :class:`cterasdk.exceptions.auth.AuthenticationError`
        """
        host = self._core.host()
        try:
            self._core.api.form_data('/login', {'j_username': username, 'j_password': password})
            logger.info("User logged in. %s", {'host': host, 'user': username})
        except Forbidden as error:
            logger.error('Login failed. %s', {'host': host, 'user': username})
            raise AuthenticationError() from error

    def sso(self, ctera_ticket):
        """
        Login using a Portal ticket.

        :param str ticket: SSO Ticket.
        """
        logger.info('Logging in using a Portal ticket.')
        self._core.ctera.form_data('/sso', {'ctera_ticket': ctera_ticket})

    def logout(self):
        """
        Log out of CTERA Portal
        """
        username = self._core.session().account.name
        try:
            self._core.api.form_data('/logout', {})
            logger.info("User logged out. %s", {'host': self._core.host(), 'user': username})
        except SessionExpired:
            logger.info("Session expired and is no longer active.")
