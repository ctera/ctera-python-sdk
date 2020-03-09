import logging

from .enum import Mode
from .base_command import BaseCommand


class AFP(BaseCommand):
    """ Gateway AFP APIs """

    def is_disabled(self):
        """ Check if the AFP server is disabled """
        return self._gateway.get('/config/fileservices/afp/mode') == Mode.Disabled

    def disable(self):
        """
        Disable AFP
        """
        logging.getLogger().info('Disabling AFP server.')

        self._gateway.put('/config/fileservices/afp/mode', Mode.Disabled)

        logging.getLogger().info('AFP server disabled.')
