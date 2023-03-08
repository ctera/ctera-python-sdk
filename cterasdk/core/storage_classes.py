import logging

from ..common import Object
from ..exception import CTERAException
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

    def all(self):
        """
        Get storage classes

        :returns: List of storage classes
        :rtype: list(cterasdk.common.object.Object)
        """
        if self._portal.session().in_tenant_context():
            return self._portal.execute('', 'getStorageClasses')
        return self._portal.get('/storageClasses')

    def get(self, name):
        """
        Get storage class

        :param str name: Storage class name, defaults to ``None``
        :returns: Storage class
        :rtype: cterasdk.common.object.Object
        """
        if not self._portal.session().in_tenant_context():
            return self._portal.get(f'/storageClasses/{name}')
        for storage_class in self.all():
            if storage_class.name == name:
                return storage_class
        raise CTERAException('Could not find storage class.', name=name)
