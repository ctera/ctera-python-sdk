import logging

from .enum import Mode
from .base_command import BaseCommand


class RSync(BaseCommand):
    """ Gateway RSync configuration """

    def is_disabled(self):
        """ Check if the Rsync server is disabled """
        return self._gateway.get('/config/fileservices/rsync/server') == Mode.Disabled

    def disable(self):
        """ Disable RSync """
        logging.getLogger().info('Disabling RSync server.')
        self._gateway.put('/config/fileservices/rsync/server', Mode.Disabled)
        logging.getLogger().info('RSync server disabled.')
