import logging

from .enum import Role, RoleResolver
from .types import RoleSettings
from .base_command import BaseCommand


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
        logging.getLogger('cterasdk.core').warning('Could not find role. %s', {'role': role})
        return None

    def modify(self, role, settings):
        """
        Modify Role

        :param cterasdk.core.enum.Role role: Role
        :param cterasdk.core.types.RoleSettings settings: Role Settings
        :returns: Updated role settings
        :rtype: cterasdk.core.types.RoleSettings
        """
        role = Roles.find(role)
        if role:
            logging.getLogger('cterasdk.core').info('Updating role settings. %s', {'role': role})
            response = self._core.api.put(f'/rolesSettings/{role}', settings.to_server_object())
            logging.getLogger('cterasdk.core').info('Role settings updated. %s', {'role': role})
            return RoleSettings.from_server_object(response)
        logging.getLogger('cterasdk.core').warning('Could not find role. %s', {'role': role})
        return None
