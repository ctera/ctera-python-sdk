import logging

from .base_command import BaseCommand
from ...exceptions import CTERAException


logger = logging.getLogger('cterasdk.edge')


class Login(BaseCommand):
    """
    CTERA Edge Filer Login APIs
    """

    async def login(self, username, password):
        host = self._edge.host()
        try:
            await self._edge.api.form_data('/login', {'username': username, 'password': password})
            logger.info("User logged in. %s", {'host': host, 'user': username})
        except CTERAException:
            logger.error("Login failed. %s", {'host': host, 'user': username})
            raise

    async def logout(self):
        """
        Log out of the portal
        """
        host = self._edge.host()
        user = self._edge.session().account.name
        try:
            await self._edge.api.form_data('/logout', {'foo': 'bar'})
            logger.info("User logged out. %s", {'host': host, 'user': user})
        except CTERAException:
            logger.error("Logout failed. %s", {'host': host, 'user': user})
            raise
