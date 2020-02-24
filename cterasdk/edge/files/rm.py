import logging


def delete(ctera_host, path):
    fullpath = path.fullpath()
    logging.getLogger().info('Deleting item. %s', {'path': fullpath})

    response = ctera_host.rm(fullpath)

    logging.getLogger().info('Item deleted. %s', {'path': fullpath})

    return response
