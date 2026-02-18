import logging

from ...core.enum import RoleResolver
from ...core.types import RoleSettings
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


class Roles(BaseCommand):
    """
    Role Settings APIs
    """

    @staticmethod
    def find(role):
        """
        Find Role
        """
        options = {k: v for k, v in RoleResolver.__dict__.items() if not k.startswith('_')}
        return options.get(role, None)

    async def get(self, role):
        """
        Get Role

        :param str role: Role
        :returns: Role settings
        :rtype: cterasdk.core.types.RoleSettings
        """
        name = Roles.find(role)
        if name:
            return RoleSettings.from_server_object(await self._core.v1.api.get(f'/rolesSettings/{name}'))
        logger.warning('Could not find role. %s', {'role': role})
        return None
