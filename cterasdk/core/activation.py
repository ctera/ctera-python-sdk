import logging

from .base_command import BaseCommand


class Activation(BaseCommand):
    """ Portal activation """

    def generate_code(self, username=None, tenant=None):
        """
        Generate device activation code

        :param str,optional username: User name used for activation, defaults to None
        :param str,optional tenant: Tenant name used for activation, defaults to None
        :return: Portal Activation Code
        :rtype: str
        """
        params = None
        if username:
            params = {'username': username}
        if tenant:
            params['portal'] = tenant

        logging.getLogger('cterasdk.core').info('Generating device activation code. %s', {'user': username, 'portal': tenant})
        response = self._core.api.get('/ssoActivation', params=params)
        logging.getLogger('cterasdk.core').info('Generated device activation code. %s', {'user': username, 'portal': tenant})

        return response.code
