import logging

from .base_command import BaseCommand
from .types import GroupAccount
from ..exceptions import CTERAException, ObjectNotFoundException
from ..common import Object
from ..common import union
from . import query


class Groups(BaseCommand):
    """
    Portal Groups Management APIs
    """

    default = ['name']

    @staticmethod
    def _build_resource_url(group_account):
        return f'/localGroups/{group_account.name}' if group_account.is_local \
            else f'/domains/{group_account.directory}/adGroups/{group_account.name}'

    def _get_entire_object(self, group_account):
        ref = Groups._build_resource_url(group_account)
        try:
            return self._core.api.get(ref)
        except CTERAException as error:
            raise CTERAException('Failed to retrieve group', error)

    def get(self, group_account, include=None):
        """
        Get a group account

        :param cterasdk.core.types.GroupAccount group_account: Group account, including the group directory and name
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: The group account, including the requested fields
        """
        baseurl = Groups._build_resource_url(group_account)
        include = union(include or [], Groups.default)
        include = ['/' + attr for attr in include]
        group_object = self._core.api.get_multi(baseurl, include)
        if group_object.name is None:
            raise ObjectNotFoundException('Could not find group', baseurl, group_directory=group_account.directory, name=group_account.name)
        return group_object

    def list_local_groups(self, include=None):
        """
        List all local groups

        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: Iterator for all local groups
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union(include or [], Groups.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._core, '/localGroups', param)

    def list_domain_groups(self, domain, include=None):
        """
        List all the groups in the domain

        :param str domain: Domain name
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: Iterator for all the domain groups
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union(include or [], Groups.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._core, f'/domains/{domain}/adGroups', param)

    def _members_reference(self, users):
        return [self._core.users.get(user, include=['baseObjectRef']).baseObjectRef for user in users]

    def add(self, name, description=None, members=None):
        """
        Create a local group

        :param str name: Group name
        :param str,optional description: Group description
        :param list(cterasdk.core.types.UserAccount),optional members: List of user group members
        """
        param = Object()
        param._classname = 'AddGroupParam'  # pylint: disable=protected-access
        param.groupData = Object()
        param.groupData._classname = 'PortalGroup'  # pylint: disable=protected-access
        param.groupData.name = name
        param.groupData.description = description
        if members:
            param.members = self._members_reference(members)

        logging.getLogger('cterasdk.core').info('Creating group. %s', {'group': name})
        response = self._core.api.execute('', 'addGroup', param)
        logging.getLogger('cterasdk.core').info('Group created. %s', {'group': name})

        return response

    def modify(self, current_groupname, new_groupname=None, description=None):
        """
        Modify a local group

        :param str current_groupname: The current group name
        :param str,optional new_groupname: New group name
        :param str,optional description: Group description
        """
        group_account = GroupAccount(current_groupname)
        group = self._get_entire_object(group_account)

        if new_groupname:
            group.name = new_groupname
        if description:
            group.description = description

        param = Object()
        param._classname = 'UpdateGroupParam'  # pylint: disable=protected-access
        param.groupData = group
        param.membersToAdd = []
        param.membersToDelete = []

        try:
            response = self._core.api.execute(f'/localGroups/{current_groupname}', 'updateGroup', param)
            logging.getLogger('cterasdk.core').info("Group modified. %s", {'group_name': group.name})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.core').error("Failed to modify group.")
            raise CTERAException('Failed to modify group', error)

    def get_members(self, group_account):
        """
        Get group members

        :param cterasdk.core.types.GroupAccount group_account: Group account
        """
        param = query.QueryParamBuilder().startFrom(0).build()
        return list(query.iterator(self._core, Groups._build_resource_url(group_account), param, 'getMembers'))

    def add_members(self, group_account, members):
        """
        Add group members

        :param cterasdk.core.types.GroupAccount group_account: Group account
        :param list(cterasdk.core.types.UserAccount) members: Users
        """
        current_members = self.get_members(group_account)
        new_members = self._members_reference(members)
        param = Object()
        param.groupData = self._get_entire_object(group_account)
        param.membersToAdd = list(set(new_members) - set(current_members))
        param.membersToDelete = []
        return self._core.api.execute(f'/localGroups/{group_account.name}', 'updateGroup', param)

    def remove_members(self, group_account, members):
        """
        Remove group members

        :param cterasdk.core.types.GroupAccount group_account: Group account
        :param list(cterasdk.core.types.UserAccount) members: Users
        """
        current_members = self.get_members(group_account)
        to_remove = self._members_reference(members)
        param = Object()
        param.groupData = self._get_entire_object(group_account)
        param.membersToAdd = []
        param.membersToDelete = list(set(current_members).intersection(set(to_remove)))
        return self._core.api.execute(f'/localGroups/{group_account.name}', 'updateGroup', param)

    def delete(self, group_account):
        """
        Delete a group

        :param cterasdk.core.types.GroupAccount group_account: Group account
        """
        logging.getLogger('cterasdk.core').info('Deleting group. %s', {'group': str(group_account.name)})
        baseurl = f'/localGroups/{group_account.name}' if group_account.is_local \
            else f'/domains/{group_account.directory}/adGroups/{group_account.name}'
        response = self._core.api.execute(baseurl, 'delete', True)
        logging.getLogger('cterasdk.core').info('Group deleted. %s', {'group': str(group_account.name)})

        return response
