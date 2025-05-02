import logging

from .base_command import BaseCommand
from ...exceptions import CTERAException


logger = logging.getLogger('cterasdk.core')


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
            logger.info("User logged in. %s", {'host': host, 'user': username})
        except CTERAException:
            logger.error("Login failed. %s", {'host': host, 'user': username})
            raise

    async def sso(self, ctera_ticket):
        """
        Login using a Portal ticket.

        :param str ticket: SSO Ticket.
        """
        logger.info('Logging in using a Portal ticket.')
        await self._core.v1.ctera.form_data('/sso', {'ctera_ticket': ctera_ticket})

    async def logout(self):
        """
        Log out of the portal
        """
        await self._core.v1.api.form_data('/logout', {})
        logger.info("User logged out. %s", {'host': self._core.host()})
