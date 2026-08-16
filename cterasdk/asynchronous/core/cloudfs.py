from .base_command import BaseCommand
from . import query
from ...core.query import QueryParamBuilder, FilterBuilder
from ...core.cloudfs import ZoneQueryParams, DevicesDelta, FoldersDelta
from ...common.utils import union


class CloudFS(BaseCommand):
    """
    CloudFS APIs

    :ivar cterasdk.core.cloudfs.CloudDrives drives: Object holding Cloud Drive Folders APIs
    """

    def __init__(self, core):
        super().__init__(core)
        self.groups = FolderGroups(self._core)
        self.drives = CloudDrives(self._core)
        self.zones = Zones(self._core)
        self.exports = Exports(self._core)


class FolderGroups(BaseCommand):
    """ Cloud Drive Folder APIs """

    default = ['name']

    async def all(self, include=None, namespaces=None):
        """
        List folder groups

        :param str,optional include: List of fields to retrieve, defaults to ['name']
        :param list[str],optional namespaces: List of namespaces to query
        :returns: Iterator for all folder groups
        """
        include = union(include or [], FolderGroups.default)

        for resource in [f'/portals/{namespace}' for namespace in namespaces] if namespaces is not None else ['']:
            param = QueryParamBuilder().include(include).build()
            async for group in query.iterator(self._core, f'{resource}/foldersGroups', param):
                yield group


class CloudDrives(BaseCommand):
    """ Cloud Drive Folder APIs """

    default = ['name']

    async def all(self, include=None, namespaces=None):
        """
        List Cloud Drive folders.

        :param str,optional include: List of fields to retrieve, defaults to ['name']
        :param list[str],optional namespaces: List of namespaces to query
        :returns: Iterator for all Cloud Drive folders
        """
        include = union(include or [], CloudDrives.default)

        for resource in [f'/portals/{namespace}' for namespace in namespaces] if namespaces is not None else ['']:
            param = QueryParamBuilder().include(include).put('includeDeleted', True).build()
            async for drive in query.iterator(self._core, f'{resource}/cloudDrives', param):
                yield drive

    async def find(self, name, owner, include=None):
        """
        Find a Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to find
        :param cterasdk.core.types.UserAccount owner: User account of the folder group owner
        :param list[str] include: List of metadata fields to include in the response

        :returns: A Cloud Drive Folder
        """
        user = await self._core.users.get(owner, ['uid'])
        include = union(include or [], CloudDrives.default)
        builder = QueryParamBuilder().include(include).ownedBy(user.uid)
        builder.addFilter(FilterBuilder('name').eq(name))
        param = builder.build()
        return query.iterator(self._core, '/cloudDrives', param)


class Zones(BaseCommand):
    """
    Portal Zones APIs
    """

    async def all(self, expand_zone=False, namespaces=None):
        """
        List Zones

        :param list[str],optional namespaces: List of namespaces to query

        :return: Iterator for all Zones
        :rtype: cterasdk.asynchronous.core.iterator.QueryAsyncIterator
        """
        for resource in [f'/portals/{namespace}' for namespace in namespaces] if namespaces is not None else ['']:
            param = QueryParamBuilder().include_classname().build()
            async for zone in query.iterator(self._core, resource, param, 'getZonesDisplayInfo'):
                if expand_zone:
                    info = await self._core.v1.api.execute(resource, 'getZoneBasicInfo', zone.zoneId)
                    zone.policyType = info.policyType
                    zone.devices = [device async for device in query.iterator(self._core, resource,
                                                                              ZoneQueryParams(info.zoneId, DevicesDelta()), 'getZoneDevices')]
                    if zone.policyType == 'selectedFolders':
                        zone.cloudfolders = [
                            volume
                            async for volume in query.iterator(
                                self._core,
                                resource,
                                ZoneQueryParams(info.zoneId, FoldersDelta()),
                                'getZoneFolders',
                            )
                        ]
                yield zone


class Exports(BaseCommand):
    """ Fusion Gateway S3 APIs """

    async def all(self, namespaces=None):
        """
        List Fusion Gateway S3 Exports

        :param str,optional include: List of fields to retrieve, defaults to ['name']
        :param list[str],optional namespaces: List of namespaces to query
        :returns: Iterator for all Fusion Gateway exports
        """
        for resource in [f'/portals/{namespace}' for namespace in namespaces] if namespaces is not None else ['']:
            for export in await self._core.v1.api.get(f'{resource}/buckets'):
                yield export
