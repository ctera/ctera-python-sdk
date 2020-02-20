import logging

from .enum import Mode


def disable(ctera_host):
    logging.getLogger().info('Disabling AFP server.')

    ctera_host.put('/config/fileservices/afp/mode', Mode.Disabled)

    logging.getLogger().info('AFP server disabled.')
