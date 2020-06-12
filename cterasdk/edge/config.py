from datetime import datetime
import logging

from ..lib import FileSystem
from .base_command import BaseCommand


class Config(BaseCommand):
    """ General gateway configuraion """

    def __init__(self, gateway):
        super().__init__(gateway)
        self._filesystem = FileSystem.instance()

    def get_location(self):
        """
        Get the location of the gateway

        :return str: The location of the gateway
        """
        return self._gateway.get('/config/device/location')

    def set_location(self, location):
        """
        Set the location of the gateway

        :param str location: New location to set
        :return str: The new location
        """
        logging.getLogger().info('Configuring device location. %s', {'location': location})
        return self._gateway.put('/config/device/location', location)

    def get_hostname(self):
        """
        Get the hostname of the gateway

        :return str: The hostname of the gateway
        """
        return self._gateway.get('/config/device/hostname')

    def set_hostname(self, hostname):
        """
        Set the hostname of the gateway

        :param str hostname: New hostname to set
        :return str: The new hostname
        """
        logging.getLogger().info('Configuring device hostname. %s', {'hostname': hostname})
        return self._gateway.put('/config/device/hostname', hostname)

    def export(self, destination=None):
        """ Export the Gateway configuration

        :param str,optional destination:
         File destination, defaults to the default directory
        """
        default_filename = self._gateway.host() + datetime.now().strftime('_%Y-%m-%dT%H_%M_%S') + '.xml'
        directory = filename = None
        if destination:
            directory, filename = self._filesystem.split_file_directory(destination)
            if not filename:
                filename = default_filename
        else:
            directory = self._filesystem.get_dirpath()
            filename = default_filename
        logging.getLogger().info('Exporting configuration. %s', {'host': self._gateway.host()})
        handle = self._gateway.openfile('/export')
        filepath = FileSystem.instance().save(directory, filename, handle)
        logging.getLogger().info('Exported configuration. %s', {'filepath': filepath})

    def is_wizard_enabled(self):
        """
        Get the current configuration of the first time wizard

        :return bool: True if the first time wizard is enabled, else False
        """
        return self._gateway.get('/config/gui/openFirstTimeWizard')

    def enable_wizard(self):
        """
        Enable the first time wizard
        """
        return self._set_wizard(True)

    def disable_wizard(self):
        """
        Disable the first time wizard
        """
        return self._set_wizard(False)

    def _set_wizard(self, state):
        logging.getLogger().info('Disabling first time wizard')
        return self._gateway.put('/config/gui/openFirstTimeWizard', state)
