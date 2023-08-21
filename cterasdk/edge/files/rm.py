import logging


def delete(ctera_host, path):
    fullpath = path.fullpath()
    logging.getLogger().info('Deleting item. %s', {'path': fullpath})

    response = ctera_host.rm(ctera_host.make_local_files_dir(fullpath))

    logging.getLogger().info('Item deleted. %s', {'path': fullpath})

    return response
