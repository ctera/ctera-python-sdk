import logging

from .enum import Mode
from .base_command import BaseCommand


class NFS(BaseCommand):

    def disable(self):

        logging.getLogger().info('Disabling NFS server.')

        self._gateway.put('/config/fileservices/nfs/mode', Mode.Disabled)

        logging.getLogger().info('NFS server disabled.')
