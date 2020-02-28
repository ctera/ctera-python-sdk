import logging

from .enum import Mode
from .base_command import BaseCommand


class AFP(BaseCommand):
    """ Gateway AFP APIs """

    def disable(self):
        """
        Disable AFP
        """
        logging.getLogger().info('Disabling AFP server.')

        self._gateway.put('/config/fileservices/afp/mode', Mode.Disabled)

        logging.getLogger().info('AFP server disabled.')
