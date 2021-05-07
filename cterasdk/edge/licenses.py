import logging

from ..exception import InputError
from .enum import License
from .base_command import BaseCommand


class Licenses(BaseCommand):
    """ Edge Filer License Configuration APIs """

    def __init__(self, gateway):
        super().__init__(gateway)
        self.local = LocalLicenses(self._gateway)

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

        :param cterasdk.edge.enum.License ctera_license: License type
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


class LocalLicenses(BaseCommand):
    """ Edge Filer Local License Configuration APIs """

    def get(self):
        """
        Retrieve a list of local licenses installed
        """
        return self._gateway.get('/config/device/licenses')

    def add(self, code):
        """
        Install a local license. Use this option when running the Edge Filer as a standalone appliance.

        :param str code: License code
        """
        logging.getLogger().info('Installing license. %s', {'code': code})
        response = self._gateway.add('/config/device/licenses', code)
        logging.getLogger().info("License added. %s", {'code': code})
        return response

    def clear(self):
        """
        Remove all local licenses
        """
        self._gateway.put('/config/device/licenses', [])
