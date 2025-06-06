from .base_command import BaseCommand
from ...common import union, Object
from ...exceptions import ObjectNotFoundException
from ...exceptions.session import ContextError


class Users(BaseCommand):
    """
    CTERA Portal User Management APIs
    """

    default = ['name', 'uid']

    async def get(self, user_account, include=None):
        """
        Get a user account

        :param cterasdk.core.types.UserAccount user_account: User account, including the user directory and user name
        :param list[str] include: List of fields to retrieve, defaults to ['name']

        :return: The user account, including the requested fields
        """
        baseurl = f'/users/{user_account.name}' if user_account.is_local \
            else f'/domains/{user_account.directory}/adUsers/{user_account.name}'
        include = union(include or [], Users.default)
        include = ['/' + attr for attr in include]
        user_object = await self._core.v1.api.get_multi(baseurl, include)
        if user_object.name is None:
            raise ObjectNotFoundException(baseurl)
        return user_object

    async def generate_ticket(self, username, tenant):
        """
        Create an SSO ticket for a user.

        :param str username: Username
        :param str portal: Tenant
        """
        if self.session().in_tenant_context():
            raise ContextError('Browse the Global Administration to invoke this API')
        param = Object()
        param.username = username
        param.portal = tenant
        return await self._core.v1.api.execute('', 'getSessionToken', param)
