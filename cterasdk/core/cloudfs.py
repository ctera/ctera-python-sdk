import logging

from . import query
from ..common import Object
from ..exception import CTERAException


class CloudFS:

    def __init__(self, Portal):
        self._CTERAHost = Portal

    def mkfg(self, name, user=None):
        return mkfg(self._CTERAHost, name, user)

    def rmfg(self, name):
        return rmfg(self._CTERAHost, name)

    def mkdir(self, name, group, owner, winacls=True):
        return mkdir(self._CTERAHost, name, group, owner, winacls)

    def delete(self, name, owner):
        return delete(self._CTERAHost, name, owner)

    def undelete(self, name, owner):
        return undelete(self._CTERAHost, name, owner)

    def find(self, name, owner, include):
        return find(self._CTERAHost, name, owner, include)

    def _files(self):
        return self._CTERAHost._files()  # pylint: disable=protected-access

    def _baseurl(self):
        return self._CTERAHost.baseurl() + self._CTERAHost._files()  # pylint: disable=protected-access

def mkdir(ctera_host, name, group, owner, winacls):
    owner = ctera_host.get('/users/' + owner + '/baseObjectRef')
    group = ctera_host.get('/foldersGroups/' + group + '/baseObjectRef')

    param = Object()
    param.name = name
    param.owner = owner
    param.group = group
    param.enableSyncWinNtExtendedAttributes = winacls

    try:
        response = ctera_host.execute('', 'addCloudDrive', param)
        logging.getLogger().info(
            'Created directory. %s',
            {'name' : name, 'owner' : param.owner, 'folder_group' : group, 'winacls' : winacls}
        )
        return response
    except CTERAException as error:
        logging.getLogger().error(
            'Cloud drive folder creation failed. %s',
            {'name' : name, 'folder_group' : group, 'owner' : owner, 'win_acls' : winacls}
        )
        raise error

def delete(ctera_host, name, owner):
    path = _dirpath(ctera_host, name, owner)
    logging.getLogger().info('Deleting cloud drive folder. %s', {'path' : path})
    ctera_host.files().delete(path)

def undelete(ctera_host, name, owner):
    path = _dirpath(ctera_host, name, owner)
    logging.getLogger().info('Restoring cloud drive folder. %s', {'path' : path})
    ctera_host.files().undelete(path)

def find(ctera_host, name, owner, include):
    builder = query.QueryParamBuilder().include(include)
    query_filter = query.FilterBuilder('name').eq(name)
    builder.addFilter(query_filter)
    param = builder.build()

    iterator = ctera_host.iterator('/cloudDrives', param)
    for cloud_folder in iterator:
        if cloud_folder.owner.endswith(owner):
            return cloud_folder

    logging.getLogger().info('Could not find cloud folder. %s', {'folder' : name, 'owner' : owner})
    raise CTERAException('Could not find cloud folder', None, folder=name, owner=owner)

def _dirpath(ctera_host, name, owner):
    owner = ctera_host.get('/users/' + owner + '/displayName')
    path = owner + '/' + name
    return path

def mkfg(ctera_host, name, user):
    param = Object()
    param.name = name
    param.disabled = True

    if user is None:
        param.owner = None
    else:
        param.owner = ctera_host.get('/users/' + user + '/baseObjectRef')

    try:
        response = ctera_host.execute('', 'createFolderGroup', param)
        logging.getLogger().info('Folder group created. %s', {'name' : name, 'owner' : param.owner})
        return response
    except CTERAException as error:
        logging.getLogger().error('Folder group creation failed. %s', {'name' : name, 'owner' : user})
        raise error

def rmfg(ctera_host, name):
    logging.getLogger().info('Deleting folder group. %s', {'name' : name})

    ctera_host.execute('/foldersGroups/' + name, 'deleteGroup', True)

    logging.getLogger().info('Folder group deleted. %s', {'name' : name})
