import logging

from .base_command import BaseCommand
from . import query, union
from ..common import Object
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
        include = union.union(include or [], ['name', 'owner'])
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
        include = union.union(include or [], ['name', 'owner'])
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

    def mkdir(self, name, group, owner, winacls=True):
        """
        Create a new directory

        :param str name: Name of the new directory
        :param str group: The Folder Group to which the directory belongs
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the new directory
        :param bool,optional winacls: Use Windows ACLs, defaults to True
        """

        owner = self._portal.users.get(owner, ['baseObjectRef']).baseObjectRef
        group = self._portal.get('/foldersGroups/' + group + '/baseObjectRef')

        param = Object()
        param.name = name
        param.owner = owner
        param.group = group
        param.enableSyncWinNtExtendedAttributes = winacls

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

    def list_folders(self, include=None, deleted=False, user=None):
        """
        List cloud drive folders

        :param str,optional include: List of fields to retrieve, defaults to ['name', 'group', 'owner']
        :param str,optional deleted: Retrieve deleted folders
        :param cterasdk.core.types.UserAccount user: User account of the cloud folder owner
        :returns: Iterator for all Cloud Drive folders
        """
        include = union.union(include or [], CloudFS.default)
        builder = query.QueryParamBuilder().include(include)
        query_filter = query.FilterBuilder('isDeleted').eq(deleted)
        builder.addFilter(query_filter)
        if user:
            uid = self._portal.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        param = builder.build()
        return query.iterator(self._portal, '/cloudDrives', param)

    def find(self, name, owner, include):
        """
        Find a  Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to find
        :param str owner: User name of the owner of the directory
        :param list[str] include: List of metadata fields to include in the response
        """
        builder = query.QueryParamBuilder().include(include)
        query_filter = query.FilterBuilder('name').eq(name)
        builder.addFilter(query_filter)
        param = builder.build()

        iterator = query.iterator(self._portal, '/cloudDrives', param)
        for cloud_folder in iterator:
            if cloud_folder.owner.endswith(owner):
                return cloud_folder

        logging.getLogger().info('Could not find cloud folder. %s', {'folder': name, 'owner': owner})
        raise CTERAException('Could not find cloud folder', None, folder=name, owner=owner)

    def _dirpath(self, name, owner):
        owner = self._portal.users.get(owner, ['displayName']).displayName
        path = owner + '/' + name
        return path
