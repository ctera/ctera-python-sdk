import logging

from .base_command import BaseCommand


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
        await self._core.v1.api.form_data('/login', {'j_username': username, 'j_password': password})
        logging.getLogger().info("User logged in. %s", {'host': self._core.host(), 'user': username})

    async def logout(self):
        """
        Log out of the portal
        """
        await self._core.v1.api.form_data('/logout', {})
        logging.getLogger().info("User logged out. %s", {'host': self._core.host()})
