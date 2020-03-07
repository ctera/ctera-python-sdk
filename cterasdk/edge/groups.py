import logging

from ..common import Object
from ..exception import InputError
from .enum import PrincipalType
from .base_command import BaseCommand


class Groups(BaseCommand):
    
    def get(self, name=None):
        """
        Get Group. If a group name was not passed as an argument, a list of all local groups will be retrieved
        :param str,optional name: Name of the group
        """
        return self._gateway.get('/config/auth/groups' +  ('' if name is None else ('/' + name)))

    def add_members(self, group, new_members):
        current_members = self._gateway.get('/config/auth/groups/' + group + '/members')

        new_member_dict = {}
        for new_member in new_members:
            if len(new_member) != 2:
                raise InputError('Invalid input', repr(new_member), '[("type", "name"), ...]')
            new_member_type, new_member_name = new_member
            new_member_type, new_member = Groups._member(new_member_type, new_member_name)
            new_member_dict[new_member_type + '#' + new_member_name] = new_member

        for current_member in current_members:
            current_member_type = current_member._classname  # pylint: disable=protected-access

            if current_member_type in [PrincipalType.LU, PrincipalType.LG]:
                current_member_name = current_member.ref
                current_member_name = current_member_name[current_member_name.rfind('#') + 1:]
            else:
                current_member_name = current_member.name

            current_member_key = current_member_type + '#' + current_member_name

            if current_member_key not in new_member_dict:
                new_member_dict[current_member_key] = current_member

        members = [v for k, v in new_member_dict.items()]

        logging.getLogger().info('Adding group members. %s', {'group': group})

        self._gateway.put('/config/auth/groups/' + group + '/members', members)

        logging.getLogger().info('Group members added. %s', {'group': group})

    def remove_members(self, group, tuples):
        current_members = self._gateway.get('/config/auth/groups/' + group + '/members')
        options = {v: k for k, v in PrincipalType.__dict__.items() if not k.startswith('_')}  # reverse

        members = []
        for current_member in current_members:
            current_member_type = current_member._classname  # pylint: disable=protected-access

            if current_member_type in [PrincipalType.LU, PrincipalType.LG]:
                current_member_name = current_member.ref
                current_member_name = current_member_name[current_member_name.rfind('#') + 1:]
            else:
                current_member_name = current_member.name

            if not (options.get(current_member_type), current_member_name) in tuples:
                members.append(current_member)

        logging.getLogger().info('Removing group members. %s', {'group': group})

        self._gateway.put('/config/auth/groups/' + group + '/members', members)

        logging.getLogger().info('Group members removed. %s', {'group': group})

    @staticmethod
    def _member(member_type, name):
        options = {k: v for k, v in PrincipalType.__dict__.items() if not k.startswith('_')}

        member = Object()
        member_type = options.get(member_type)

        if member_type == PrincipalType.LU:
            member._classname = PrincipalType.LU  # pylint: disable=protected-access
            member.ref = "#config#auth#users#" + name
        elif member_type == PrincipalType.LG:
            member._classname = PrincipalType.LG  # pylint: disable=protected-access
            member.ref = "#config#auth#groups#" + name
        elif member_type == PrincipalType.DU:
            member._classname = PrincipalType.DU  # pylint: disable=protected-access
            member.name = name
        elif member_type == PrincipalType.DG:
            member._classname = PrincipalType.DG  # pylint: disable=protected-access
            member.name = name
        else:
            raise InputError('Invalid principal type', member_type, list(options.keys()))

        return member_type, member
