import logging

from .enum import Mode
from .base_command import BaseCommand


class FTP(BaseCommand):
    """ Gateway FTP configuration APIs """

    def disable(self):
        """ Disable FTP """
        logging.getLogger().info('Disabling FTP server.')

        self._gateway.put('/config/fileservices/ftp/mode', Mode.Disabled)

        logging.getLogger().info('FTP server disabled.')
