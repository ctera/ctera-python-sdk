import logging

from ..common import Object
from .base_command import BaseCommand


class Drive(BaseCommand):
    """
    Gateway Drive APIs
    """

    def get(self, name=None):
        """
        Get Drive. If a drive name was not passed as an argument, a list of all drives will be retrieved

        :param str,optional name: Name of the drive
        """
        return self._gateway.get('/config/storage/disks' + ('' if name is None else ('/' + name)))

    def get_status(self, name=None):
        """
        Get drive status. If a drive name was not passed as an argument, a list of all drives will be retrieved

        :param str name: Name of the drive
        """
        return self._gateway.get('/status/storage/disks' + ('' if name is None else ('/' + name)))

    def format(self, name):
        """
        Format a drive

        :param str name: The name of the drive to format
        """
        param = Object()
        param.name = name

        self._gateway.execute("/proc/storage", "format", param)

        logging.getLogger().info('Formatting drive. %s', {'drive': name})

    def format_all(self):
        """ Format all drives """
        drives = self._gateway.get('/status/storage/disks')

        for drive in drives:
            self.format(drive.name)
