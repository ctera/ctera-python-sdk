import logging

from ..common import Object
from ..exception import CTERAException


def add(ctera_host, array_name, level, *args):
    param = Object()
    param.name = array_name
    param.level = level
    param.members = list(args)

    try:
        logging.getLogger().info("Creating a storage array.")
        response = ctera_host.add("/config/storage/arrays", param)
        logging.getLogger().info("Storage array created.")
        return response
    except CTERAException as error:
        logging.getLogger().error("Storage array creation failed.")
        raise CTERAException("Storage array creation failed.", error)


def delete(ctera_host, array_name):
    try:
        logging.getLogger().info("Deleting a storage array.")
        response = ctera_host.delete("/config/storage/arrays/" + array_name)
        logging.getLogger().info("Storage array deleted. %s", {'array_name': array_name})
        return response
    except CTERAException as error:
        logging.getLogger().error("Storage array deletion failed.")
        raise CTERAException("Storage array deletion failed.", error)


def delete_all(ctera_host):
    arrays = ctera_host.get('/config/storage/arrays')
    for array in arrays:
        delete(ctera_host, array.name)
