import logging

from ..common import Object
from ..exceptions import CTERAException
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Array(BaseCommand):
    """ Edge Filer Array APIs """

    def get(self, name=None):
        """
        Get Array. If an array name was not passed as an argument, a list of all arrays will be retrieved

        :param str,optional name: Name of the array
        """
        return self._edge.api.get('/config/storage/arrays' + ('' if name is None else ('/' + name)))

    def add(self, array_name, level, members=None):
        """
        Add a new array

        :param str array_name: Name for the new array
        :param RAIDLevel level: RAID level
        :param list(str) members: Members of the array. If not specified, the system will try to create an array using all available drives
        """
        param = Object()
        param.name = array_name
        param.level = level
        param.members = [drive.name for drive in self._edge.drive.get_status()] if members is None else members

        try:
            ref = "/config/storage/arrays"
            logger.info("Creating a storage array.")
            response = self._edge.api.add(ref, param)
            logger.info("Storage array created: %s/%s", ref, array_name)
            return response
        except CTERAException as error:
            logger.error("Storage array creation failed: %s", array_name)
            raise CTERAException(f"Storage array creation failed: {array_name}") from error

    def delete(self, array_name):
        """
        Delete an array

        :param str name: The name of the array to delete
        """
        ref = f"/config/storage/arrays/{array_name}"
        try:
            logger.info("Deleting a storage array.")
            response = self._edge.api.delete(ref)
            logger.info("Storage array deleted: %s", ref)
            return response
        except CTERAException as error:
            logger.error("Storage array deletion failed: %s", ref)
            raise CTERAException(f"Storage array deletion failed: {ref}") from error

    def delete_all(self):
        """
        Delete all arrays
        """
        arrays = self._edge.api.get('/config/storage/arrays')
        for array in arrays:
            self.delete(array.name)
