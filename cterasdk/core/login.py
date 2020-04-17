import logging

from .base_command import BaseCommand


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
        self._portal.form_data('/login', {'j_username': username, 'j_password': password})
        logging.getLogger().info("User logged in. %s", {'host': self._portal.host(), 'user': username})

    def logout(self):
        """
        Log out of the portal
        """
        self._portal.form_data('/logout', {})
        logging.getLogger().info("User logged out. %s", {'host': self._portal.host()})
