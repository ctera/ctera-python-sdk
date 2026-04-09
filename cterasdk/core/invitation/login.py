import logging
from ..base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


class Login(BaseCommand):
    """
    Portal Login APIs
    """

    def login(self, key, value):
        logger.info('Creating external session. %s', {'invite': value})
        self._core.clients.ctera.get('', params={key: value})

    def logout(self):
        """No logout for external users"""
