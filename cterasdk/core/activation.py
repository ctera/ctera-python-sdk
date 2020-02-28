import logging

from .base_command import BaseCommand
from ..convert import tojsonstr


class Activation(BaseCommand):
    """ Portal activation """

    def generate_code(self, username, tenant):
        """
        Generate device activation code

        :param username: User name used for activation
        :type username: str
        :param tenant: Tenant name used for activation
        :type tenant: str

        :return: Portal Activation Code
        :rtype: str
        """
        params = {'username': username}

        if tenant is not None:
            params['portal'] = tenant

        logging.getLogger().info('Generating device activation code. %s', {'user': username, 'portal': tenant})

        response = self._portal.get('/ssoActivation', params)

        logging.getLogger().info('Generated device activation code. %s', tojsonstr(response, False))

        return response.code
