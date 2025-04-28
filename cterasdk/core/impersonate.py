from .base_command import BaseCommand
from ..common import Object


class Impersonate(BaseCommand):
    """
    Portal User Impersonation APIs
    """

    def session_token(self, username, tenant):
        """
        Impersonate a Portal User.

        :param str username: Username
        :param str portal: Tenant
        """
        param = Object()
        param.username = username
        param.portal = tenant
        return self._core.api.execute('', 'getSessionToken', param)
