import logging

from .base_command import BaseCommand
from ...exceptions.transport import InternalServerError
from ...exceptions.auth import AuthenticationError


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
        except InternalServerError as e:
            logger.error("Login failed. %s", {'host': host, 'user': username})
            if e.error.response.error.msg == 'Wrong username or password':
                raise AuthenticationError() from e
            raise

    async def logout(self):
        """
        Log out of the portal
        """
        host = self._edge.host()
        user = self._edge.session().account.name
        await self._edge.api.form_data('/logout', {'foo': 'bar'})
        logger.info("User logged out. %s", {'host': host, 'user': user})
