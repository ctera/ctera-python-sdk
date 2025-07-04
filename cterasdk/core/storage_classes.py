import logging

from ..common import Object
from ..exceptions import CTERAException
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


class StorageClasses(BaseCommand):
    """ Portal Storage Classes APIs """

    def add(self, name):
        """
        Add a storage class

        :param str name: Name
        """
        logger.info("Adding storage class. %s", {'name': name})
        param = Object()
        param.name = name
        response = self._core.api.add('/storageClasses', param)
        logger.info("Storage class added. %s", {'name': name})
        return response

    def all(self):
        """
        Get storage classes

        :returns: List of storage classes
        :rtype: list(cterasdk.common.object.Object)
        """
        if self._core.session().in_tenant_context():
            return self._core.api.execute('', 'getStorageClasses')
        return self._core.api.get('/storageClasses')

    def get(self, name):
        """
        Get storage class

        :param str name: Storage class name, defaults to ``None``
        :returns: Storage class
        :rtype: cterasdk.common.object.Object
        """
        ref = f'/storageClasses/{name}'
        if not self._core.session().in_tenant_context():
            return self._core.api.get(ref)
        for storage_class in self.all():
            if storage_class.name == name:
                return storage_class
        raise CTERAException(f'Storage class not found: {ref}')
