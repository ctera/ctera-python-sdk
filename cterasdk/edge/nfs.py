import logging

from .enum import Mode
from .base_command import BaseCommand


class NFS(BaseCommand):
    """ Gateway NFS configuration """

    def disable(self):
        """ Disable NFS """

        logging.getLogger().info('Disabling NFS server.')

        self._gateway.put('/config/fileservices/nfs/mode', Mode.Disabled)

        logging.getLogger().info('NFS server disabled.')
