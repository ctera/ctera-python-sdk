import logging

from .base_command import BaseCommand


class Config(BaseCommand):
    """ General gateway configuraion """

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

    def disable_wizard(self):
        """
        Disable the first time wizard
        """
        logging.getLogger().info('Disabling first time wizard')
        return self._gateway.put('/config/gui/openFirstTimeWizard', False)
