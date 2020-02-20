import logging

from ..common import Object


def format_drive(ctera_host, name):
    '''
    {
        "desc": "Format a drive"
    }
    '''
    param = Object()
    param.name = name

    ctera_host.execute("/proc/storage", "format", param)

    logging.getLogger().info('Formatting drive. %s', {'drive': name})


def format_all(ctera_host):
    '''
    {
        "desc": "Format all drives"
    }
    '''
    drives = ctera_host.get('/status/storage/disks')

    for drive in drives:
        format_drive(ctera_host, drive.name)
