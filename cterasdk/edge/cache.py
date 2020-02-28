import logging

from .enum import OperationMode
from .base_command import BaseCommand


class Cache(BaseCommand):
    """ Gateway cache configuration """

    def enable(self):
        """ Enable caching """
        logging.getLogger().info('Enabling caching.')
        self._set_operation_mode(OperationMode.CachingGateway)

    def disable(self):
        """ Disable caching """
        logging.getLogger().info('Disabling caching.')
        self._set_operation_mode(OperationMode.Disabled)

    def force_eviction(self):
        """ Force eviction """
        logging.getLogger().info("Starting file eviction.")
        self._gateway.execute("/config/cloudsync", "forceExecuteEvictor", None)
        logging.getLogger().info("Eviction started.")

    def _set_operation_mode(self, mode):
        self._gateway.put('/config/cloudsync/cloudExtender/operationMode', mode)
        logging.getLogger().info('Device opreation mode changed. %s', {'mode': mode})
