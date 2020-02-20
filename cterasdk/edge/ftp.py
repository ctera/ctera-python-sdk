import logging

from .enum import Mode


def disable(ctera_host):
    logging.getLogger().info('Disabling FTP server.')

    ctera_host.put('/config/fileservices/ftp/mode', Mode.Disabled)

    logging.getLogger().info('FTP server disabled.')
