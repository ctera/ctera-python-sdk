import logging

from .enum import Mode
from .base_command import BaseCommand


class FTP(BaseCommand):
    """ Gateway FTP configuration APIs """
    
    def is_disabled(self):
        """ Check if the FTP server is disabled """
        return (self._gateway.get('/config/fileservices/ftp/mode') == Mode.Disabled)

    def disable(self):
        """ Disable FTP """
        logging.getLogger().info('Disabling FTP server.')

        self._gateway.put('/config/fileservices/ftp/mode', Mode.Disabled)

        logging.getLogger().info('FTP server disabled.')
