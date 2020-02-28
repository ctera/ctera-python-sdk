import logging

from ..common import Object
from .base_command import BaseCommand


class Drive(BaseCommand):
    """
    Gateway Drive APIs
    """

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
