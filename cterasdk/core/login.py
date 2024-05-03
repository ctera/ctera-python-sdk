import logging

from .base_command import BaseCommand
from ..exceptions import CTERAException


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
            logging.getLogger('cterasdk.core').info("User logged in. %s", {'host': host, 'user': username})
        except CTERAException:
            logging.getLogger('cterasdk.core').error('Login failed. %s', {'host': host, 'user': username})
            raise

    def logout(self):
        """
        Log out of the portal
        """
        username = self._core.session().user.name
        self._core.api.form_data('/logout', {})
        logging.getLogger('cterasdk.core').info("User logged out. %s", {'host': self._core.host(), 'user': username})
