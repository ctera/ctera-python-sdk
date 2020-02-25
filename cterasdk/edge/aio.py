import logging
from .base_command import BaseCommand


class AIO(BaseCommand):

    def enable(self):
        logging.getLogger().info('Enabling asynchronous io.')
        self._async_io(True, 1, 1)
        logging.getLogger().info('Asynchronous io enabled.')

    def disable(self):
        logging.getLogger().info('Disabling asynchronous io.')
        self._async_io(False, 0, 0)
        logging.getLogger().info('Asynchronous io disabled.')

    def _async_io(self, robustMutexes, aioReadThreshold, aioWriteThreshold):
        logging.getLogger().debug('Obtaining CIFS server settings.')

        cifs = self._gateway.get('/config/fileservices/cifs')
        cifs.robustMutexes = robustMutexes
        cifs.aioReadThreshold = aioReadThreshold
        cifs.aioWriteThreshold = aioWriteThreshold

        logging.getLogger().debug('Updating CIFS server settings.')

        self._gateway.put('/config/fileservices/cifs', cifs)
