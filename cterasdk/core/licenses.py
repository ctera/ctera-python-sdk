import logging

from ..common import Object
from .base_command import BaseCommand


class Licenses(BaseCommand):
    """
    Portal Licenses APIs
    """

    def all(self):
        """
        Retrieve a list of installed licenses

        :returns: A list of licenses
        :rtype: list[cterasdk.common.object.Object]
        """
        return self._portal.get('/portalLicenses')

    def add(self, *keys):
        """
        Add license keys

        :param list[str] keys: List of license keys
        """
        logging.getLogger().info('Adding license(s)')
        param = Object()
        param.keys = list(keys)
        self._portal.execute('', 'addLicenses', param)
        logging.getLogger().info('License(s) added')

    def remove(self, *keys):
        """
        Remove license keys

        :returns: A list of installed licenses
        :rtype: list[cterasdk.common.object.Object]
        """
        licenses = self.all()
        param = [license for license in licenses if license.key not in keys and license.originalKey not in keys]
        if len(param) != len(licenses):
            logging.getLogger().info('Updating licenses.')
            response = self._portal.put('/portalLicenses', param)
            logging.getLogger().info('Licenses updated.')
            return response
        return None
