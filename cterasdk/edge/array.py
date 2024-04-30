import logging

from ..common import Object
from ..exceptions import CTERAException
from .base_command import BaseCommand


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
            logging.getLogger('cterasdk.edge').info("Creating a storage array.")
            response = self._edge.api.add("/config/storage/arrays", param)
            logging.getLogger('cterasdk.edge').info("Storage array created.")
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.edge').error("Storage array creation failed.")
            raise CTERAException("Storage array creation failed.", error)

    def delete(self, array_name):
        """
        Delete an array

        :param str name: The name of the array to delete
        """
        try:
            logging.getLogger('cterasdk.edge').info("Deleting a storage array.")
            response = self._edge.api.delete("/config/storage/arrays/" + array_name)
            logging.getLogger('cterasdk.edge').info("Storage array deleted. %s", {'array_name': array_name})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.edge').error("Storage array deletion failed.")
            raise CTERAException("Storage array deletion failed.", error)

    def delete_all(self):
        """
        Delete all arrays
        """
        arrays = self._edge.api.get('/config/storage/arrays')
        for array in arrays:
            self.delete(array.name)
