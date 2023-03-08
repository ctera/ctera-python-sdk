import logging

from ..common import Object
from .base_command import BaseCommand


class StorageClasses(BaseCommand):
    """ Portal Storage Classes APIs """

    def add(self, name):
        """
        Add a storage class

        :param str name: Name
        """
        logging.getLogger().info("Adding storage class. %s", {'name': name})
        param = Object()
        param.name = name
        response = self._portal.add('/storageClasses', param)
        logging.getLogger().info("Storage class added. %s", {'name': name})
        return response

    def get(self):
        """
        Get storage classes

        :returns: List of storage classes
        :rtype: list(cterasdk.common.object.Object)
        """
        if self._portal.session().in_tenant_context():
            return self._portal.execute('', 'getStorageClasses')
        return self._portal.get('/storageClasses')
