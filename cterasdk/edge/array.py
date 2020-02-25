import logging

from ..common import Object
from ..exception import CTERAException
from .base_command import BaseCommand


class Array(BaseCommand):

    def add(self, array_name, level, *args):
        param = Object()
        param.name = array_name
        param.level = level
        param.members = list(args)

        try:
            logging.getLogger().info("Creating a storage array.")
            response = self._gateway.add("/config/storage/arrays", param)
            logging.getLogger().info("Storage array created.")
            return response
        except CTERAException as error:
            logging.getLogger().error("Storage array creation failed.")
            raise CTERAException("Storage array creation failed.", error)

    def delete(self, array_name):
        try:
            logging.getLogger().info("Deleting a storage array.")
            response = self._gateway.delete("/config/storage/arrays/" + array_name)
            logging.getLogger().info("Storage array deleted. %s", {'array_name': array_name})
            return response
        except CTERAException as error:
            logging.getLogger().error("Storage array deletion failed.")
            raise CTERAException("Storage array deletion failed.", error)

    def delete_all(self):
        arrays = self._gateway.get('/config/storage/arrays')
        for array in arrays:
            self.delete(array.name)
