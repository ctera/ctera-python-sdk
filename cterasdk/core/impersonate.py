from .base_command import BaseCommand
from ..common import Object


class Impersonate(BaseCommand):
    """
    Portal User Impersonation APIs
    """

    def impersonate(self, username, tenant):
        """
        Impersonate a Portal User.

        :param str username: Username
        :param str portal: Tenant
        """
        param = Object()
        param.username = username
        param.portal = tenant
        ticket = self._core.api.execute('', 'getSessionToken', param)
        #user = objects.ServicesPortal(self._core.host(), self._core.port())
        #user.sso(ticket)
        #return user
        return ticket
