import re
import copy
import logging

from .base_command import BaseCommand
from . import query, devices
from .enum import ListFilter, PolicyType
from .types import ComplianceSettingsBuilder, ExtendedAttributesBuilder
from ..common import union, Object
from ..exceptions import CTERAException, ObjectNotFoundException


logger = logging.getLogger('cterasdk.core')


class CloudFS(BaseCommand):
    """
    CloudFS APIs

    :ivar cterasdk.core.cloudfs.FolderGroups groups: Object holding Folder Groups APIs
    :ivar cterasdk.core.cloudfs.CloudDrives drives: Object holding Cloud Drive Folders APIs
    :ivar cterasdk.core.cloudfs.Backups backups: Object holding Backup Folders APIs
    :ivar cterasdk.core.cloudfs.Zones zones: Object holding Zones APIs
    :ivar cterasdk.core.cloudfs.Exports exports: Object holding Bucket Exports APIs
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.groups = FolderGroups(self._core)
        self.drives = CloudDrives(self._core)
        self.backups = Backups(self._core)
        self.zones = Zones(self._core)
        self.exports = Exports(self._core)


class FolderGroups(BaseCommand):
    """ Folder Groups APIs """

    default = ['name', 'owner']

    def _get_entire_object(self, name):
        ref = f'/foldersGroups/{name}'
        try:
            return self._core.api.get(ref)
        except CTERAException as error:
            raise CTERAException(f'Folder group not found: {ref}') from error

    def get(self, name, include=None):
        """
        Get folder group

        :param str name: Name of the Folder Group to find
        :param str,optional include: List of fields to retrieve, defaults to ['name', 'owner']
        """
        include = union(include or [], FolderGroups.default)
        include = ['/' + attr for attr in include]
        folder_group = self._core.api.get_multi(f'/foldersGroups/{name}', include)
        if folder_group.name is None:
            raise ObjectNotFoundException(f'/foldersGroups/{name}')
        return folder_group

    def all(self, include=None, user=None):
        """
        List folder groups

        :param str,optional include: List of fields to retrieve, defaults to ['name', 'owner']
        :param cterasdk.core.types.UserAccount user: User account of the folder group owner
        :returns: Iterator for all folder groups
        """
        include = union(include or [], FolderGroups.default)
        builder = query.QueryParamBuilder().include(include)
        if user:
            uid = self._core.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        param = builder.build()
        return query.iterator(self._core, '/foldersGroups', param)

    def add(self, name, user=None, deduplication_method_type=None, storage_class=None):
        """
        Create a Folder Group

        :param str name: Name of the new folder group
        :param cterasdk.core.types.UserAccount user:
         User account, the user directory and name of the new folder group owner (default to None)
        :param cterasdk.core.enum.DeduplicationMethodType deduplication_method_type: Deduplication-Method
        :param str,optional storage_class: Storage class, defaults to the Default storage class
        """

        param = Object()
        param.name = name
        param.disabled = False
        param.owner = self._core.users.get(user, ['baseObjectRef']).baseObjectRef if user is not None else None
        param.deduplicationMethodType = deduplication_method_type
        if storage_class:
            param.storageClass = self._core.storage_classes.get(storage_class).baseObjectRef

        try:
            response = self._core.api.execute('', 'createFolderGroup', param)
            logger.info('Folder group created. %s', {'name': name, 'owner': param.owner})
            return response
        except CTERAException as error:
            logger.error('Folder group creation failed. %s', {'name': name, 'owner': str(user)})
            raise error

    def modify(self, current_name, new_name):
        """
        Modify a folder group

        :param str current_name: Current folder group name
        :param str new_name: New folder group name
        """
        param = self._get_entire_object(current_name)
        if new_name:
            param.name = new_name

        ref = f'/foldersGroups/{current_name}'
        try:
            response = self._core.api.put(ref, param)
            logger.info('Folder group modified: %s', current_name)
            return response
        except CTERAException as error:
            logger.error('Folder group modification failed: %s', current_name)
            raise CTERAException(f'Folder group modification failed: {ref}') from error

    def delete(self, name):
        """
        Remove a Folder Group

        :param str name: Name of the folder group to remove
        """

        logger.info('Deleting folder group. %s', {'name': name})
        self._core.api.execute('/foldersGroups/' + name, 'deleteGroup', True)
        logger.info('Folder group deleted. %s', {'name': name})


class CloudDrives(BaseCommand):
    """ Cloud Drive Folder APIs """

    default = ['name', 'group', 'owner']

    def _get_entire_object(self, name, owner):
        return self._core.api.get(f'{self.find(name, owner, include=["baseObjectRef"]).baseObjectRef}')

    def add(self, name, group, owner, winacls=True, description=None, quota=None, compliance_settings=None, xattrs=None):
        """
        Create a new Cloud Drive Folder (Cloud Volume)

        :param str name: Name of the new folder
        :param str group: Folder Group to assign this folder to
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the new folder
        :param bool,optional winacls: Use Windows ACLs, defaults to True
        :param str,optional description: Cloud drive folder description
        :param str,optional quota: Cloud drive folder quota in GB
        :param cterasdk.common.object.Object,optional compliance_settings: Compliance settings, defaults to disabled.
         Use :func:`cterasdk.core.types.ComplianceSettingsBuilder` to build the compliance settings object
        :param cterasdk.common.object.Object,optional xattrs: Extended attributes, defaults to MacOS.
         Use :func:`cterasdk.core.types.ExtendedAttributesBuilder` to build the extended attributes object
        """
        param = Object()
        param.name = name
        param.owner = self._core.users.get(owner, ['baseObjectRef']).baseObjectRef
        param.group = self._core.cloudfs.groups.get(group, ['baseObjectRef']).baseObjectRef
        param.enableSyncWinNtExtendedAttributes = winacls
        param.folderQuota = quota
        if description:
            param.description = description
        param.wormSettings = compliance_settings if compliance_settings else ComplianceSettingsBuilder.default().build()
        if xattrs:
            param.extendedAttributes = xattrs
        elif not winacls:  # Only override default when winacls is False
            param.extendedAttributes = Object()
            param.extendedAttributes._classname = 'ExtendedAttributes'  # pylint: disable=protected-access
            param.extendedAttributes.enable = False
            param.extendedAttributes.attributes = [Object()]
            param.extendedAttributes.attributes[0]._classname = 'ExtendedAttributesInfo'  # pylint: disable=protected-access
            param.extendedAttributes.attributes[0].name = 'MacOS'
            param.extendedAttributes.attributes[0].supported = True
        else:
            param.extendedAttributes = ExtendedAttributesBuilder.default().build()

        try:
            response = self._core.api.execute('', 'addCloudDrive', param)
            logger.info(
                'Cloud drive folder created. %s',
                {'name': name, 'owner': param.owner, 'folder_group': group, 'winacls': winacls}
            )
            return response
        except CTERAException as error:
            logger.error(
                'Cloud drive folder creation failed. %s',
                {'name': name, 'folder_group': group, 'owner': owner, 'win_acls': winacls}
            )
            raise error

    def modify(self, current_name, owner, new_name=None, new_owner=None, new_group=None,  # pylint: disable=too-many-arguments
               description=None, winacls=None, quota=None, compliance_settings=None, xattrs=None):
        """
        Modify a Cloud Drive Folder (Cloud Volume)

        :param str current_name: Current folder name
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the folder
        :param str,optional new_name: New folder name
        :param cterasdk.core.types.UserAccount,optional new_owner: User account, the new owner of the folder
        :param str,optional new_group: Folder Group to assign this folder to
        :param str,optional description: Folder description
        :param bool,optional winacls: Enable or disable Windows ACLs
        :param str,optional quota: Folder quota in GB
        :param cterasdk.common.object.Object,optional compliance_settings: Compliance settings.
         Use :func:`cterasdk.core.types.ComplianceSettingsBuilder` to build the compliance settings object
        :param cterasdk.common.object.Object,optional xattrs: Extended attributes.
         Use :func:`cterasdk.core.types.ExtendedAttributesBuilder` to build the extended attributes object
        """
        param = self._get_entire_object(current_name, owner)
        if new_name:
            param.name = new_name
        if new_owner:
            param.owner = self._core.users.get(new_owner, ['baseObjectRef']).baseObjectRef
        if new_group:
            param.group = self._core.cloudfs.groups.get(new_group, include=['baseObjectRef']).baseObjectRef
        if description:
            param.description = description
        if winacls:
            param.enableSyncWinNtExtendedAttributes = winacls
        if quota:
            param.folderQuota = quota
        if compliance_settings:
            param.wormSettings = compliance_settings
        if xattrs:
            param.extendedAttributes = xattrs
        try:
            response = self._core.api.put(f'/{param.baseObjectRef}', param)
            logger.info('Cloud drive folder updated. %s', {'name': current_name})
            return response
        except CTERAException as error:
            logger.error('Cloud drive folder update failed. %s', {'name': current_name})
            raise error

    def all(self, include=None, list_filter=ListFilter.NonDeleted, user=None):
        """
        List Cloud Drive folders.

        :param str,optional include: List of fields to retrieve, defaults to ['name', 'group', 'owner']
        :param cterasdk.core.enum.ListFilter list_filter: Filter the list of Cloud Drive folders, defaults to non-deleted folders
        :param cterasdk.core.types.UserAccount user: User account of the cloud folder owner
        :returns: Iterator for all Cloud Drive folders
        """
        include = union(include or [], CloudDrives.default)
        builder = query.QueryParamBuilder().include(include)
        if list_filter != ListFilter.NonDeleted:
            builder.put('includeDeleted', True)
            if list_filter == ListFilter.Deleted:
                query_filter = query.FilterBuilder('isDeleted').eq(True)
                builder.addFilter(query_filter)
        if user:
            uid = self._core.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        param = builder.build()
        return query.iterator(self._core, '/cloudDrives', param)

    def find(self, name, owner, include=None):
        """
        Find a Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to find
        :param cterasdk.core.types.UserAccount owner: Cloud drive folder owner
        :param list[str] include: List of metadata fields to include in the response

        :returns: A Cloud Drive Folder
        """
        include = union(include or [], CloudDrives.default)
        builder = query.QueryParamBuilder().include(include)
        builder.addFilter(query.FilterBuilder('name').eq(name))
        builder.addFilter(query.FilterBuilder('owner', True).eq(owner.name))
        builder.put('includeDeleted', True)
        param = builder.build()

        iterator = query.iterator(self._core, '/cloudDrives', param)
        try:
            return next(iterator)
        except StopIteration:
            logger.info('Could not find cloud folder. %s', {'folder': name, 'owner': str(owner)})
            raise CTERAException(f"Unable to locate the Cloud Drive folder '{name}' owned by '{str(owner)}.")

    def delete(self, name, owner, *, permanently=False):
        """
        Delete a Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to delete
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the Cloud Drive Folder to delete
        :param bool,optional permanently: Delete permanently
        """
        cloudfolder = self.find(name, owner, include=['uid', 'isDeleted'])
        logger.info('Deleting cloud drive folder. %s', {'name': name, 'owner': str(owner), 'permanently': permanently})
        if permanently:
            return self._core.api.execute(f'/objs/{cloudfolder.uid}', 'deleteFolderPermanently')
        if not cloudfolder.isDeleted:
            return self._core.api.execute(f'/objs/{cloudfolder.uid}', 'delete')
        logger.info('Cloud Drive folder was already deleted. %s', {'name': cloudfolder.name})
        return None

    def recover(self, name, owner):
        """
        Recover a deleted a Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to un-delete
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the Cloud Drive Folder to delete
        """
        display_name = self._core.users.get(owner, ['displayName']).displayName
        logger.info('Recovering cloud drive folder. %s', {'name': name, 'owner': str(owner)})
        return self._core.files.undelete(f'Users/{display_name}/{name}')

    def setfacl(self, paths, acl, recursive=False):
        """
        Changing the file or folder ACLs

        :param list(str) paths:  List of folder paths
        :param str acl: Access control list (ACL) represented as an SDDL String
        :param bool,optional recursive: Apply changes recursively to subfolders and files
        """
        param = Object()
        param._classname = 'SDDLFoldersParam'  # pylint: disable=protected-access
        param.foldersPath = paths
        param.sddlString = acl
        param.isRecursive = recursive
        try:
            return self._core.api.execute('', 'setFoldersACL', param)
        except CTERAException as error:
            logger.error('An error occurred attempting to update access control entries.')
            raise CTERAException('ACL modification failed.') from error

    def setoacl(self, paths, owner_sid, recursive=False):
        """
        Changing the File or Folder Owner SID or ACLs

        :param list(str) paths:  List of folder paths
        :param str owner_sid: Owner SID (Security Descriptor)
        :param bool,optional recursive: Apply changes recursively to subfolders and files
        """
        param = Object()
        param._classname = 'OwnerSidFoldersParam'  # pylint: disable=protected-access
        param.foldersPath = paths
        param.ownerSid = owner_sid
        param.isRecursive = recursive
        try:
            return self._core.api.execute('', 'setOwnerACL', param)
        except CTERAException as error:
            logger.error('An error occurred attempting to update owner.')
            raise CTERAException('Owner modification failed.') from error


class Backups(BaseCommand):
    """ Backup Folder APIs """

    default = ['name', 'group', 'owner']

    def _get_entire_object(self, name):
        return self._core.api.get(f'/backups/{name}')

    def add(self, name, group, owner, xattr=True):
        """
        Create a new Backup Folder

        :param str name: Name of the backup folder
        :param str group: Folder Group to assign this folder to
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the backup folder
        :param bool,optional xattr: Backup extended attributes, defaults to True
        """
        param = Object()
        param._classname = 'Backup'  # pylint: disable=protected-access
        param.name = name
        param.owner = self._core.users.get(owner, ['baseObjectRef']).baseObjectRef
        param.group = self._core.cloudfs.groups.get(group, ['baseObjectRef']).baseObjectRef
        param.enableBackupExtendedAttributes = xattr
        try:
            response = self._core.api.add('/backups', param)
            logger.info(
                'Backup folder created. %s',
                {'name': name, 'owner': param.owner, 'folder_group': group, 'xattr': xattr}
            )
            return response
        except CTERAException as error:
            logger.error(
                'Backup folder creation failed. %s',
                {'name': name, 'folder_group': group, 'owner': owner, 'xattr': xattr}
            )
            raise error

    def modify(self, current_name, new_name=None, new_owner=None, new_group=None, xattr=None):
        """
        Modify a Backup Folder

        :param str current_name: Current folder name
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the folder
        :param str,optional new_name: New folder name
        :param cterasdk.core.types.UserAccount,optional new_owner: User account, the new owner of the folder
        :param str,optional new_group: Folder Group to assign this folder to
        :param bool,optional xattr: Backup extended attributes
        """
        param = self._get_entire_object(current_name)
        if new_name:
            param.name = new_name
        if new_owner:
            param.owner = self._core.users.get(new_owner, ['baseObjectRef']).baseObjectRef
        if new_group:
            param.group = self._core.cloudfs.groups.get(new_group, include=['baseObjectRef']).baseObjectRef
        if xattr:
            param.enableBackupExtendedAttributes = xattr
        try:
            response = self._core.api.put(f'/backups/{current_name}', param)
            logger.info('Backup folder updated. %s', {'name': current_name})
            return response
        except CTERAException as error:
            logger.error('Backup folder update failed. %s', {'name': current_name})
            raise error

    def all(self, include=None, list_filter=ListFilter.NonDeleted, user=None):
        """
        List Backup folders.

        :param str,optional include: List of fields to retrieve, defaults to ['name', 'group', 'owner']
        :param cterasdk.core.enum.ListFilter list_filter: Filter the list of Backup folders, defaults to non-deleted folders
        :param cterasdk.core.types.UserAccount user: Filter by backup folder owner
        :returns: Iterator for all Backup folders
        """
        include = union(include or [], Backups.default)
        builder = query.QueryParamBuilder().include(include)
        if list_filter != ListFilter.NonDeleted:
            builder.put('includeDeleted', True)
            if list_filter == ListFilter.Deleted:
                query_filter = query.FilterBuilder('isDeleted').eq(True)
                builder.addFilter(query_filter)
        if user:
            uid = self._core.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        param = builder.build()
        return query.iterator(self._core, '/backups', param)

    def delete(self, name):
        """
        Delete a Backup Folder

        :param str name: Name of the Backup Folder to delete
        """
        logger.info('Deleting Backup folder. %s', {'name': name})
        response = self._core.api.execute(f'/backups/{name}', 'delete')
        logger.info('Backup folder deleted. %s', {'name': name})
        return response


class Zones(BaseCommand):
    """
    Portal Zones APIs
    """

    name_attr = 'name'

    def get(self, name):
        """
        Get zone by name

        :param str name: The name of the zone to get
        :return: The requested zone
        """
        query_filter = query.FilterBuilder('name').eq(name)
        param = query.QueryParamBuilder().include_classname().startFrom(0).countLimit(1).addFilter(query_filter).orFilter(False).build()

        logger.info('Retrieving zone. %s', {'name': name})

        response = self._core.api.execute('', 'getZonesDisplayInfo', param)

        objects = response.objects
        if len(objects) < 1:
            logger.error('Zone not found. %s', {'name': name})
            raise CTERAException(f'Zone not found: {name}')

        zone = objects[0]
        logger.info('Zone found. %s', {'name': name, 'id': zone.zoneId})
        return zone

    def all(self, filters=None):
        """
        List Zones
        :param list[],optional filters: List of additional filters, defaults to None

        :return: Iterator for all Zones
        :rtype: cterasdk.lib.iterator.Iterator
        """
        builder = query.QueryParamBuilder().include_classname().startFrom(0).countLimit(25)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        builder.orFilter((len(filters) > 1))
        param = builder.build()
        return query.iterator(self._core, '', param, 'getZonesDisplayInfo')

    def search(self, name):
        """
        Search for Zones by name
        :param str name: Search query

        :return: Iterator for all matching Zones
        :rtype: cterasdk.lib.iterator.Iterator
        """
        filters = [query.FilterBuilder(Zones.name_attr).like(name)]
        return self.all(filters)

    def add(self, name, policy_type=PolicyType.SELECT, description=None):
        """
        Add a new zone

        :param str name: The name of the new zone
        :param cterasdk.core.enum.PolicyType,optional policy_type:
         Policy type of the new zone, defaults to cterasdk.core.enum.PolicyType.SELECT
        :param str,optional description: The description of the new zone
        """
        param = self._zone_param(name, policy_type, description)

        logger.info('Adding zone. %s', {'name': name})

        response = self._core.api.execute('', 'addZone', param)
        try:
            self._process_response(response)
            logger.info('Zone added. %s', {'name': name})
        except CTERAException as error:
            logger.error('Zone creation failed. %s', {'rc': response.rc})
            raise error

    def delete(self, name):
        """
        Delete a zone

        :param str name: The name of the zone to delete
        """
        zone = self._core.cloudfs.zones.get(name)
        logger.info('Deleting zone. %s', {'zone': name})
        response = self._core.api.execute('', 'deleteZones', [zone.zoneId])
        if response == 'ok':
            logger.info('Zone deleted. %s', {'zone': name})

    def add_devices(self, name, device_names):
        """
        Add devices to a zone

        :param str name: The name of the zone to add devices to
        :param list[str] device_names: The names of the devices to add to the zone
        """
        zone = self._core.cloudfs.zones.get(name)
        portal_devices = devices.Devices(self._core).by_name(include=['uid'], names=device_names)
        info = self._zone_info(zone.zoneId)
        description = (info.description if hasattr(info, 'description') else None)

        param = self._zone_param(info.name, info.policyType, description, info.zoneId)
        for portal_device in portal_devices:
            param.delta.devicesDelta.added.append(portal_device.uid)

        logger.info('Adding devices to zone. %s', {'zone': info.name})

        try:
            self._save(param)
        except CTERAException as error:
            logger.error('Failed adding devices to zone.')
            raise CTERAException(f"Failed adding devices: [{', '.join(device_names)}] to zone: {name}") from error

    def add_folders(self, name, folder_finding_helpers):
        """
        Add the folders to the zone

        :param str name: The name of the zone
        :param list[cterasdk.core.types.CloudFSFolderFindingHelper] folder_finding_helpers: List of folder names and owners
        """
        zone = self._core.cloudfs.zones.get(name)
        folders = self._find_folders(folder_finding_helpers)
        info = self._zone_info(zone.zoneId)
        description = info.description if hasattr(info, 'description') else None
        param = self._zone_param(info.name, info.policyType, description, info.zoneId)
        param.delta.policyDelta = []

        for owner_id, folder_ids in folders.items():
            policyDelta = Object()
            policyDelta._classname = 'ZonePolicyDelta'  # pylint: disable=protected-access
            policyDelta.userUid = owner_id
            policyDelta.foldersDelta = Object()
            policyDelta.foldersDelta._classname = 'ZoneFolderDelta'  # pylint: disable=protected-access
            policyDelta.foldersDelta.added = copy.deepcopy(folder_ids)
            policyDelta.foldersDelta.removed = []

            param.delta.policyDelta.append(policyDelta)

        try:
            self._save(param)
        except CTERAException as error:
            logger.error('Failed adding folders to zone.')
            raise CTERAException(f'Failed adding folders to zone: {name}') from error

    def _zone_info(self, zid):
        logger.debug('Obtaining zone info. %s', {'id': zid})
        response = self._core.api.execute('', 'getZoneBasicInfo', zid)
        logger.debug('Obtained zone info. %s', {'id': zid})
        return response

    def _find_folders(self, folder_finding_helpers):
        folders = {}
        for folder_finding_helper in folder_finding_helpers:
            cloud_folder = CloudDrives(self._core).find(
                folder_finding_helper.name,
                folder_finding_helper.owner,
                include=['uid', 'owner']
            )
            folder_id = cloud_folder.uid
            owner_id = re.search("[1-9][0-9]*", cloud_folder.owner).group(0)

            if folders.get(owner_id) is None:
                folders[owner_id] = [folder_id]
            else:
                folders.get(owner_id).append(folder_id)

        return folders

    def _save(self, param):
        zone_name = param.basicInfo.name

        logger.debug('Applying changes to zone. %s', {'zone': param.basicInfo.name})

        response = self._core.api.execute('', 'saveZone', param)
        try:
            self._process_response(response)
        except CTERAException as error:
            logger.error('Failed applying changes to zone. %s', {'zone': zone_name, 'rc': response.rc})
            raise error

        logger.debug('Zone changes applied successfully. %s', {'zone': zone_name})

    @staticmethod
    def _process_response(response):
        if response.rc != 'OK':
            raise CTERAException(f'Zone creation failed: {response}')

    @staticmethod
    def _zone_param(name, policy_type, description=None, zid=None):
        param = Object()
        param._classname = "SaveZoneParam"  # pylint: disable=protected-access
        param.basicInfo = Object()
        param.basicInfo._classname = 'ZoneBasicInfo'  # pylint: disable=protected-access
        param.basicInfo.name = name
        param.basicInfo.policyType = policy_type
        param.basicInfo.description = description
        param.basicInfo.zoneId = zid
        param.delta = Object()
        param.delta._classname = 'ZoneDelta'  # pylint: disable=protected-access
        param.delta.devicesDelta = Object()
        param.delta.devicesDelta._classname = 'ZoneDeviceDelta'  # pylint: disable=protected-access
        param.delta.devicesDelta.added = []
        param.delta.devicesDelta.removed = []
        return param


class Exports(BaseCommand):
    """ S3 Exports APIs """

    def get(self, name):
        """
        Get Buckets

        :param str name: Bucket name
        """
        return self._core.api.get(f'/buckets/{name}')

    def get_endpoint(self, name):
        """
        Get Endpoint

        :param str name: Bucket name
        :returns: Bucket endpoint
        :rtype: str
        """
        return self.get(name).url

    def all(self):
        """
        List Buckets
        """
        param = query.QueryParamBuilder().startFrom(0).countLimit(25).orFilter(True).build()
        return query.iterator(self._core, '/buckets', param)

    def add(self, name, drive_name, drive_owner, description=None):
        """
        Add Bucket

        :param str name: Bucket name
        :param str drive_name: Cloud Drive Folder name
        :param str drive_owner: Cloud Drive Folder owner
        :param str,optional description: Bucket description
        """
        param = Object()
        param._classname = 'Bucket'  # pylint: disable=protected-access
        param.description = description
        param.name = name
        param.cloudDrive = self._core.cloudfs.drives.find(drive_name, drive_owner, include=['baseObjectRef']).baseObjectRef
        logger.info('Adding Bucket. %s', {'name': name})
        response = self._core.api.add('/buckets', param)
        logger.info('Bucket Added. %s', {'name': name})
        return response

    def modify(self, name, description):
        """
        Modify Bucket

        :param str name: Bucket name
        :param str description: Bucket description
        """

        bucket = self.get(name)
        bucket.description = description
        logger.info("Modifying Bucket. %s", {'name': name})
        response = self._core.api.put(f'/buckets/{name}', bucket)
        logger.info("Bucket modified. %s", {'name': name})
        return response

    def delete(self, name):
        """
        Remove Bucket

        :param str name: Bucket name
        """
        logger.info('Deleting Bucket. %s', {'name': name})
        response = self._core.api.delete(f'/buckets/{name}')
        logger.info('Bucket deleted. %s', {'name': name})
        return response
