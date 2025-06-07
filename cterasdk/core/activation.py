import logging

from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


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

        logger.info('Generating device activation code. %s', {'user': username, 'portal': tenant})
        response = self._core.api.get('/ssoActivation', params=params)
        logger.info('Generated device activation code. %s', {'user': username, 'portal': tenant})

        return response.code
