import logging

from .enum import Mode
from .base_command import BaseCommand


class FTP(BaseCommand):

    def disable(self):
        logging.getLogger().info('Disabling FTP server.')

        self._gateway.put('/config/fileservices/ftp/mode', Mode.Disabled)

        logging.getLogger().info('FTP server disabled.')
