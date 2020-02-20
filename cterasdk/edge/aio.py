import logging


def enable(ctera_host):
    logging.getLogger().info('Enabling asynchronous io.')

    async_io(ctera_host, True, 1, 1)

    logging.getLogger().info('Asynchronous io enabled.')


def disable(ctera_host):
    logging.getLogger().info('Disabling asynchronous io.')

    async_io(ctera_host, False, 0, 0)

    logging.getLogger().info('Asynchronous io disabled.')


def async_io(ctera_host, robustMutexes, aioReadThreshold, aioWriteThreshold):
    logging.getLogger().debug('Obtaining CIFS server settings.')

    cifs = ctera_host.get('/config/fileservices/cifs')
    cifs.robustMutexes = robustMutexes
    cifs.aioReadThreshold = aioReadThreshold
    cifs.aioWriteThreshold = aioWriteThreshold

    logging.getLogger().debug('Updating CIFS server settings.')

    ctera_host.put('/config/fileservices/cifs', cifs)
