import logging

from .enum import Mode
from .base_command import BaseCommand


class RSync(BaseCommand):
    """ Gateway RSync configuration """

    def disable(self):
        """ Disable RSync """
        logging.getLogger().info('Disabling RSync server.')
        self._gateway.put('/config/fileservices/rsync/server', Mode.Disabled)
        logging.getLogger().info('RSync server disabled.')
