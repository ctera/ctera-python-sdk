import logging

from ..exception import InputError
from .enum import License
from .base_command import BaseCommand


class Licenses(BaseCommand):
    """ Gateway License configuration APIs """

    @staticmethod
    def infer(ctera_license):
        if License.__dict__.get(ctera_license) is None:
            logging.getLogger().error('Invalid license type. %s', {'license': ctera_license})
            options = [v for k, v in License.__dict__.items() if not k.startswith('_')]
            raise InputError('Invalid license type', ctera_license, options)

        ctera_license = License.__dict__.get(ctera_license)
        return 'vGateway' + ('' if ctera_license == 'EV16' else ctera_license[2:])

    def apply(self, ctera_license):
        """
        Apply a license

        :param str ctera_license
        """
        inferred_license = Licenses.infer(ctera_license)

        logging.getLogger().info('Applying license. %s', {'license': ctera_license})

        self._gateway.put('/config/device/activeLicenseType', inferred_license)

        logging.getLogger().info('License applied. %s', {'license': ctera_license})

    def get(self):
        """
        Get the current Gateway License
        """
        inferred_license = self._gateway.get('/config/device/activeLicenseType')
        if inferred_license == 'NA':
            return inferred_license
        if len(inferred_license) == 8:
            inferred_license = inferred_license + '16'
        return 'EV' + inferred_license[8:]
