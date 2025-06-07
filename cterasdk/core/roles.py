import logging

from .enum import Role, RoleResolver
from .types import RoleSettings
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


class Roles(BaseCommand):
    """
    Role Settings APIs
    """

    @staticmethod
    def types():
        """
        Get a list of roles
        """
        return [v for k, v in Role.__dict__.items() if not k.startswith('_')]

    @staticmethod
    def find(role):
        """
        Find Role
        """
        options = {k: v for k, v in RoleResolver.__dict__.items() if not k.startswith('_')}
        return options.get(role, None)

    def get(self, role):
        """
        Get Role

        :param str role: Role
        :returns: Role settings
        :rtype: cterasdk.core.types.RoleSettings
        """
        role = Roles.find(role)
        if role:
            return RoleSettings.from_server_object(self._core.api.get(f'/rolesSettings/{role}'))
        logger.warning('Could not find role. %s', {'role': role})
        return None

    def modify(self, role, settings):
        """
        Modify Role

        :param cterasdk.core.enum.Role role: Role
        :param cterasdk.core.types.RoleSettings settings: Role Settings
        :returns: Updated role settings
        :rtype: cterasdk.core.types.RoleSettings
        """
        name = role
        role = Roles.find(role)
        if role:
            if settings.sudo:
                settings = RoleSettings(name=name, **{attr: True for attr in settings.__dict__.keys() if attr != 'name'})
            logger.info('Updating role settings. %s', {'role': role})
            response = self._core.api.put(f'/rolesSettings/{role}', settings.to_server_object())
            logger.info('Role settings updated. %s', {'role': role})
            return RoleSettings.from_server_object(response)
        logger.warning('Could not find role. %s', {'role': role})
        return None
