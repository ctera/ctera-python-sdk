import logging

from .enum import Mode
from .base_command import BaseCommand


class NFS(BaseCommand):
    """ Gateway NFS configuration """

    def is_disabled(self):
        """ Check if the NFS server is disabled """
        return self._gateway.get('/config/fileservices/nfs/mode') == Mode.Disabled

    def disable(self):
        """ Disable NFS """

        logging.getLogger().info('Disabling NFS server.')

        self._gateway.put('/config/fileservices/nfs/mode', Mode.Disabled)

        logging.getLogger().info('NFS server disabled.')
