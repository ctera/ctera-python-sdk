import logging

from ..common import Object
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


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
        return self._core.api.get('/portalLicenses')

    def add(self, *keys):
        """
        Add license keys

        :param list[str] keys: List of license keys
        """
        logger.info('Adding license(s)')
        param = Object()
        param.keys = list(keys)
        self._core.api.execute('', 'addLicenses', param)
        logger.info('License(s) added')

    def remove(self, *keys):
        """
        Remove license keys

        :returns: A list of installed licenses
        :rtype: list[cterasdk.common.object.Object]
        """
        licenses = self.all()
        param = [license for license in licenses if license.key not in keys and license.originalKey not in keys]
        if len(param) != len(licenses):
            logger.info('Updating licenses.')
            response = self._core.api.put('/portalLicenses', param)
            logger.info('Licenses updated.')
            return response
        return None
