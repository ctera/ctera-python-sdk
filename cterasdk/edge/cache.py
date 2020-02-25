import logging

from .enum import OperationMode
from .base_command import BaseCommand


class Cache(BaseCommand):

    def enable(self):
        logging.getLogger().info('Enabling caching.')
        self._set_operation_mode(OperationMode.CachingGateway)

    def disable(self):
        logging.getLogger().info('Disabling caching.')
        self._set_operation_mode(OperationMode.Disabled)

    def force_eviction(self):
        logging.getLogger().info("Starting file eviction.")
        self._gateway.execute("/config/cloudsync", "forceExecuteEvictor", None)
        logging.getLogger().info("Eviction started.")

    def _set_operation_mode(self, mode):
        self._gateway.put('/config/cloudsync/cloudExtender/operationMode', mode)
        logging.getLogger().info('Device opreation mode changed. %s', {'mode': mode})
