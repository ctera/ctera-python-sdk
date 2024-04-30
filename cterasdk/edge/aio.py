import logging
from .base_command import BaseCommand


class AIO(BaseCommand):
    """
    Edge Filer AIO APIs
    """
    def is_enabled(self):
        """
        Is AIO enabled

        :return: True is AIO is enabled, else False
        :rtype: bool
        """
        cifs = self._edge.api.get('/config/fileservices/cifs')
        return cifs.robustMutexes and (cifs.aioReadThreshold > 0) and (cifs.aioWriteThreshold > 0)

    def enable(self):
        """
        Enable AIO
        """
        logging.getLogger('cterasdk.edge').info('Enabling asynchronous io.')
        self._async_io(True, 1, 1)
        logging.getLogger('cterasdk.edge').info('Asynchronous io enabled.')

    def disable(self):
        """
        Disable AIO
        """
        logging.getLogger('cterasdk.edge').info('Disabling asynchronous io.')
        self._async_io(False, 0, 0)
        logging.getLogger('cterasdk.edge').info('Asynchronous io disabled.')

    def _async_io(self, robustMutexes, aioReadThreshold, aioWriteThreshold):
        logging.getLogger('cterasdk.edge').debug('Obtaining CIFS server settings.')

        cifs = self._edge.api.get('/config/fileservices/cifs')
        cifs.robustMutexes = robustMutexes
        cifs.aioReadThreshold = aioReadThreshold
        cifs.aioWriteThreshold = aioWriteThreshold

        logging.getLogger('cterasdk.edge').debug('Updating CIFS server settings.')

        self._edge.api.put('/config/fileservices/cifs', cifs)
