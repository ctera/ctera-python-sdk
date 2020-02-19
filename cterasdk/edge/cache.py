from .enum import OperationMode

import logging

def enable(ctera_host):
    
    logging.getLogger().info('Enabling caching.')

    _set_operation_mode(ctera_host, OperationMode.CachingGateway)

def disable(ctera_host):
    
    logging.getLogger().info('Disabling caching.')

    _set_operation_mode(ctera_host, OperationMode.Disabled)
    
def _set_operation_mode(ctera_host, mode):
    
    ctera_host.put('/config/cloudsync/cloudExtender/operationMode', mode)
    
    logging.getLogger().info('Device opreation mode changed. {0}'.format({'mode' : mode}))

def force_eviction(ctera_host):
    
    logging.getLogger().info("Starting file eviction.")

    ctera_host.execute("/config/cloudsync", "forceExecuteEvictor", None)

    logging.getLogger().info("Eviction started.")