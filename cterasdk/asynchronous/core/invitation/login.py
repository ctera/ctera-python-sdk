import logging
from ..base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


class Login(BaseCommand):
    """
    Portal Login APIs
    """

    async def login(self, key, value):
        logger.info('Creating external session. %s', {'invite': value})
        await self._core.clients.v1.ctera.get('', params={key: value})

    async def logout(self):
        """No logout for external users"""
