import logging

from ..exception import InputError
from .base_command import BaseCommand
from .types import UserGroupEntry


class Groups(BaseCommand):

    def get(self, name=None):
        """
        Get Group. If a group name was not passed as an argument, a list of all local groups will be retrieved

        :param str,optional name: Name of the group
        """
        return self._gateway.get('/config/auth/groups' + ('' if name is None else ('/' + name)))

    def add_members(self, group, members):
        """
        Add members to a group

        :param str group: Name of the group
        :param list[cterasdk.edge.types.UserGroupEntry] members: List of users and groups to add to the group
        """
        Groups._validate_members(members)
        new_member_dict = {
            member.principal_type + '#' + member.name: member.to_server_object()
            for member in members
        }

        current_members = self._gateway.get('/config/auth/groups/' + group + '/members')
        for current_member in current_members:
            user_group_entry = UserGroupEntry.from_server_object(current_member)
            user_group_entry_key = user_group_entry.principal_type + '#' + user_group_entry.name
            if user_group_entry_key not in new_member_dict:
                new_member_dict[user_group_entry_key] = current_member

        members = [v for k, v in new_member_dict.items()]

        logging.getLogger().info('Adding group members. %s', {'group': group})

        self._gateway.put('/config/auth/groups/' + group + '/members', members)

        logging.getLogger().info('Group members added. %s', {'group': group})

    def remove_members(self, group, members):
        """
        Remove members from a group

        :param str group: Name of the group
        :param list[cterasdk.edge.types.UserGroupEntry] members: List of users and groups to remove from the group
        """
        Groups._validate_members(members)
        remove_members_dict = {
            member.principal_type + '#' + member.name: True
            for member in members
        }

        current_members = self._gateway.get('/config/auth/groups/' + group + '/members')
        members = []
        for member in current_members:
            user_group_entry = UserGroupEntry.from_server_object(member)
            if not remove_members_dict.get(user_group_entry.principal_type + '#' + user_group_entry.name, False):
                members.append(member)

        logging.getLogger().info('Removing group members. %s', {'group': group})

        self._gateway.put('/config/auth/groups/' + group + '/members', members)

        logging.getLogger().info('Group members removed. %s', {'group': group})

    @staticmethod
    def _validate_members(members):
        if not isinstance(members, list):
            raise InputError('Invalid members list format', repr(members), '[cterasdk.edge.types.UserGroupEntry, ...]')
        for member in members:
            if not isinstance(member, UserGroupEntry):
                raise InputError('Invalid access control entry format', repr(member), 'cterasdk.edge.types.UserGroupEntry')
