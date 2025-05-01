import logging

from .base_command import BaseCommand
from ..exceptions import CTERAException


logger = logging.getLogger('cterasdk.core')


class Login(BaseCommand):
    """
    Portal Login APIs
    """

    def login(self, username, password):
        """
        Log into the portal

        :param str username: User name to log in
        :param str password: User password
        """
        host = self._core.host()
        try:
            self._core.api.form_data('/login', {'j_username': username, 'j_password': password})
            logger.info("User logged in. %s", {'host': host, 'user': username})
        except CTERAException:
            logger.error('Login failed. %s', {'host': host, 'user': username})
            raise

    def sso(self, ticket):
        """
        Single Sign On

        :param str ticket: SSO Ticket.
        """
        logger.info('Single Sign On.')
        self._core.ctera.form_data('/sso', {'ctera_ticket': ticket})

    def logout(self):
        """
        Log out of the portal
        """
        username = self._core.session().account.name
        self._core.api.form_data('/logout', {})
        logger.info("User logged out. %s", {'host': self._core.host(), 'user': username})
