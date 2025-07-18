import logging

from ..common import Object
from .types import DeduplicationStatus
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Dedup(BaseCommand):
    """ Edge Filer Local Deduplication APIs """

    def __init__(self, edge):
        super().__init__(edge)
        self.regen = Regeneration(self._edge)

    def is_enabled(self):
        """
        Check if deduplication is enabled

        :return: True is deduplication is enabled, else False
        :rtype: bool
        """
        response = self._edge.api.get('/config/dedup/useLocalMapFileDedup')
        return False if response is None else response

    def enable(self, reboot=False, wait=False):
        """
        Enable local deduplication

        :param bool reboot: Reboot, defaults to ``False``
        :param bool,optional wait: Wait for reboot to complete, defaults to False
        """
        logger.info("Enabling local deduplication.")
        response = self._edge.api.put('/config/dedup/useLocalMapFileDedup', True)
        self._wait_for_reboot(reboot, wait)
        return response

    def disable(self, reboot=False, wait=False):
        """
        Disable local deduplication

        :param bool reboot: Reboot, defaults to ``False``
        :param bool,optional wait: Wait for reboot to complete, defaults to False
        """
        logger.info("Disabling local deduplication.")
        response = self._edge.api.put('/config/dedup/useLocalMapFileDedup', False)
        self._wait_for_reboot(reboot, wait)
        return response

    def status(self):
        """
        Get the de-duplication status

        :returns: An object including the deduplication status
        :rtype: cterasdk.edge.types.DeduplicationStatus
        """
        size = self._edge.api.execute('/config/cloudsync/cloudExtender', 'allFilesTotalUsedBytes')
        usage = self._edge.api.execute('/config/cloudsync/cloudExtender', 'storageUsedBytes')
        return DeduplicationStatus(size, usage)

    def _wait_for_reboot(self, reboot, wait):
        if reboot:
            self._edge.power.reboot(wait)


class Regeneration(BaseCommand):
    """ Edge Filer Local Deduplication Regeneration APIs """

    def run(self):
        """
        Run the regeneration process
        """
        logger.info("Executing the dedup regeneration process.")
        return self._edge.api.execute('/config/dedup', 'regenerate', Object())

    def status(self):
        """
        Get the regeneration process statistics
        """
        return self._edge.api.get('/proc/dedup/regenerate/general')
