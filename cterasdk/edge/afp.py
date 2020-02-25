import logging

from .enum import Mode
from .base_command import BaseCommand


class AFP(BaseCommand):

    def disable(self):
        logging.getLogger().info('Disabling AFP server.')

        self._gateway.put('/config/fileservices/afp/mode', Mode.Disabled)

        logging.getLogger().info('AFP server disabled.')
