import logging

from .base_command import BaseCommand


class Config(BaseCommand):

    def get_location(self):
        return self._gateway.get('/config/device/location')

    def set_location(self, location):
        logging.getLogger().info('Configuring device location. %s', {'location': location})
        return self._gateway.put('/config/device/location', location)

    def get_hostname(self):
        return self._gateway.get('/config/device/hostname')

    def set_hostname(self, hostname):
        logging.getLogger().info('Configuring device hostname. %s', {'hostname': hostname})
        return self._gateway.put('/config/device/hostname', hostname)
