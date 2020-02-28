import logging

from ..common import Object
from ..exception import CTERAException
from .base_command import BaseCommand


class Array(BaseCommand):
    """ Gateway Array APIs """

    def add(self, array_name, level, members):
        """
        Add a new array

        :param str array_name: Name for the new array
        :param str level:
        :param list(str) members: Members of the array
        """
        param = Object()
        param.name = array_name
        param.level = level
        param.members = members

        try:
            logging.getLogger().info("Creating a storage array.")
            response = self._gateway.add("/config/storage/arrays", param)
            logging.getLogger().info("Storage array created.")
            return response
        except CTERAException as error:
            logging.getLogger().error("Storage array creation failed.")
            raise CTERAException("Storage array creation failed.", error)

    def delete(self, array_name):
        """
        Delete an array

        :param str name: The name of the array to delete
        """
        try:
            logging.getLogger().info("Deleting a storage array.")
            response = self._gateway.delete("/config/storage/arrays/" + array_name)
            logging.getLogger().info("Storage array deleted. %s", {'array_name': array_name})
            return response
        except CTERAException as error:
            logging.getLogger().error("Storage array deletion failed.")
            raise CTERAException("Storage array deletion failed.", error)

    def delete_all(self):
        """
        Delete all arrays
        """
        arrays = self._gateway.get('/config/storage/arrays')
        for array in arrays:
            self.delete(array.name)
