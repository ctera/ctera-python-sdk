import logging

from .base_command import BaseCommand
from ..convert import tojsonstr


class Activation(BaseCommand):
    def generate_code(self, username, tenant):
        params = {'username': username}

        if tenant is not None:
            params['portal'] = tenant

        logging.getLogger().info('Generating device activation code. %s', {'user': username, 'portal': tenant})

        response = self._portal.get('/ssoActivation', params)

        logging.getLogger().info('Generated device activation code. %s', tojsonstr(response, False))

        return response.code
