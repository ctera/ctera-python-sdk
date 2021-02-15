import logging

from .base_command import BaseCommand
from . import query
from .enum import ListFilter
from ..common import Object
from ..common import union
from ..exception import CTERAException


class CloudFS(BaseCommand):
    """ CloudFS APIs """

    default = ['name', 'group', 'owner']

    def get(self, name, include=None):
        """
        Get folder group

        :param str name: Name of the Folder Group to find
        :param str,optional include: List of fields to retrieve, defaults to ['name', 'owner']
        """
        include = union(include or [], ['name', 'owner'])
        include = ['/' + attr for attr in include]
        folder_group = self._portal.get_multi('/foldersGroups/' + name, include)
        if folder_group.name is None:
            raise CTERAException('Could not find folder group', None, name=name)
        return folder_group

    def list_folder_groups(self, include=None, user=None):
        """
        List folder groups

        :param str,optional include: List of fields to retrieve, defaults to ['name', 'owner']
        :param cterasdk.core.types.UserAccount user: User account of the folder group owner
        :returns: Iterator for all folder groups
        """
        include = union(include or [], ['name', 'owner'])
        builder = query.QueryParamBuilder().include(include)
        if user:
            uid = self._portal.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        param = builder.build()
        return query.iterator(self._portal, '/foldersGroups', param)

    def mkfg(self, name, user=None):
        """
        Create a new Folder Group

        :param str name: Name of the new folder group
        :param cterasdk.core.types.UserAccount user:
         User account, the user directory and name of the new folder group owner (default to None)
        """

        param = Object()
        param.name = name
        param.disabled = True
        param.owner = self._portal.users.get(user, ['baseObjectRef']).baseObjectRef if user is not None else None

        try:
            response = self._portal.execute('', 'createFolderGroup', param)
            logging.getLogger().info('Folder group created. %s', {'name': name, 'owner': param.owner})
            return response
        except CTERAException as error:
            logging.getLogger().error('Folder group creation failed. %s', {'name': name, 'owner': user})
            raise error

    def rmfg(self, name):
        """
        Remove a Folder Group

        :param str name: Name of the folder group to remove
        """

        logging.getLogger().info('Deleting folder group. %s', {'name': name})
        self._portal.execute('/foldersGroups/' + name, 'deleteGroup', True)
        logging.getLogger().info('Folder group deleted. %s', {'name': name})

    def mkdir(self, name, group, owner, winacls=True, description=None):
        """
        Create a new directory

        :param str name: Name of the new directory
        :param str group: The Folder Group to which the directory belongs
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the new directory
        :param bool,optional winacls: Use Windows ACLs, defaults to True
        :param str,optional description: Cloud drive folder description
        """

        owner = self._portal.users.get(owner, ['baseObjectRef']).baseObjectRef
        group = self._portal.get('/foldersGroups/' + group + '/baseObjectRef')

        param = Object()
        param.name = name
        param.owner = owner
        param.group = group
        param.enableSyncWinNtExtendedAttributes = winacls
        if description:
            param.description = description

        try:
            response = self._portal.execute('', 'addCloudDrive', param)
            logging.getLogger().info(
                'Created directory. %s',
                {'name': name, 'owner': param.owner, 'folder_group': group, 'winacls': winacls}
            )
            return response
        except CTERAException as error:
            logging.getLogger().error(
                'Cloud drive folder creation failed. %s',
                {'name': name, 'folder_group': group, 'owner': owner, 'win_acls': winacls}
            )
            raise error

    def delete(self, name, owner):
        """
        Delete a Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to delete
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the Cloud Drive Folder to delete
        """

        path = self._dirpath(name, owner)
        logging.getLogger().info('Deleting cloud drive folder. %s', {'path': path})
        self._portal.files.delete(path)

    def undelete(self, name, owner):
        """
        Un-Delete a Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to un-delete
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the Cloud Drive Folder to delete
        """
        path = self._dirpath(name, owner)
        logging.getLogger().info('Restoring cloud drive folder. %s', {'path': path})
        self._portal.files.undelete(path)

    def list_folders(self, include=None, list_filter=ListFilter.NonDeleted, user=None):
        """
        List Cloud Drive folders.

        :param str,optional include: List of fields to retrieve, defaults to ['name', 'group', 'owner']
        :param cterasdk.core.enum.ListFilter list_filter: Filter the list of Cloud Drive folders, defaults to non-deleted folders
        :param cterasdk.core.types.UserAccount user: User account of the cloud folder owner
        :returns: Iterator for all Cloud Drive folders
        """
        include = union(include or [], CloudFS.default)
        builder = query.QueryParamBuilder().include(include)
        if list_filter != ListFilter.NonDeleted:
            builder.put('includeDeleted', True)
            if list_filter == ListFilter.Deleted:
                query_filter = query.FilterBuilder('isDeleted').eq(True)
                builder.addFilter(query_filter)
        if user:
            uid = self._portal.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        param = builder.build()
        return query.iterator(self._portal, '/cloudDrives', param)

    def find(self, name, owner, include=None):
        """
        Find a Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to find
        :param cterasdk.core.types.UserAccount owner: User account of the folder group owner
        :param list[str] include: List of metadata fields to include in the response

        :returns: A Cloud Drive Folder
        """

        uid = self._portal.users.get(owner, ['uid']).uid
        include = union(include or [], CloudFS.default)
        builder = query.QueryParamBuilder().include(include).ownedBy(uid)
        builder.addFilter(query.FilterBuilder('name').eq(name))
        param = builder.build()

        iterator = query.iterator(self._portal, '/cloudDrives', param)
        try:
            return next(iterator)
        except StopIteration:
            logging.getLogger().info('Could not find cloud folder. %s', {'folder': name, 'owner': str(owner)})
            raise CTERAException('Could not find cloud folder', None, folder=name, owner=str(owner))

    def _dirpath(self, name, owner):
        owner = self._portal.users.get(owner, ['displayName']).displayName
        path = owner + '/' + name
        return path
