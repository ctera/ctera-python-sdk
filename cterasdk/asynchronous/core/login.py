import logging

from .base_command import BaseCommand
from ...exceptions import CTERAException


class Login(BaseCommand):
    """
    CTERA Portal Login APIs
    """

    async def login(self, username, password):
        """
        Log into the portal

        :param str username: User name to log in
        :param str password: User password
        """
        host = self._core.host()
        try:
            await self._core.v1.api.form_data('/login', {'j_username': username, 'j_password': password})
            logging.getLogger().info("User logged in. %s", {'host': host, 'user': username})
        except CTERAException:
            logging.getLogger().error("Login failed. %s", {'host': host, 'user': username})
            raise

    async def logout(self):
        """
        Log out of the portal
        """
        await self._core.v1.api.form_data('/logout', {})
        logging.getLogger().info("User logged out. %s", {'host': self._core.host()})
