import logging

from ..exception import InputError
from .enum import License


def infer(ctera_license):
    if License.__dict__.get(ctera_license) is None:
        logging.getLogger().error('Invalid license type. %s', {'license' : ctera_license})
        options = [v for k, v in License.__dict__.items() if not k.startswith('_')]
        raise InputError('Invalid license type', ctera_license, options)

    ctera_license = License.__dict__.get(ctera_license)
    return 'vGateway' + ('' if ctera_license == 'EV16' else ctera_license[2:])


def apply(ctera_host, ctera_license):
    inferred_license = infer(ctera_license)

    logging.getLogger().info('Applying license. %s', {'license' : ctera_license})

    ctera_host.put('/config/device/activeLicenseType', inferred_license)

    logging.getLogger().info('License applied. %s', {'license' : ctera_license})
