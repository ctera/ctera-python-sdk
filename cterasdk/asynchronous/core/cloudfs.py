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
        self.drives = CloudDrives(self._core)
        self.zones = Zones(self._core)


class CloudDrives(BaseCommand):
    """ Cloud Drive Folder APIs """

    default = ['name']

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

    async def all(self, filters=None):
        """
        List Zones
        :param list[],optional filters: List of additional filters, defaults to None

        :return: Iterator for all Zones
        :rtype: cterasdk.lib.iterator.QueryIterator
        """
        builder = QueryParamBuilder().include_classname().startFrom(0).countLimit(25)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        builder.orFilter((len(filters) > 1))
        param = builder.build()
        async for zone in query.iterator(self._core, '', param, 'getZonesDisplayInfo'):
            yield zone

    async def list_zones(self, filters=None, expand_zone=False):
        """
        List Zones
        :param list[],optional filters: List of additional filters, defaults to None
        :param bool,optional expand_zone: Include Cloud Drive folders and devices

        :return: Iterator for all Zones
        :rtype: cterasdk.lib.iterator.QueryIterator
        """
        async for zone in self.all(filters):
            if expand_zone:
                info = await self._core.v1.api.execute('', 'getZoneBasicInfo', zone.zoneId)
                zone.devices = [device async for device in query.iterator(self._core, '',
                                                                          ZoneQueryParams(info.zoneId, DevicesDelta()), 'getZoneDevices')]
                if info.policyType == 'selectedFolders':
                    zone.cloudfolders = [volume async for volume in query.iterator(self._core, '',
                                                                                   ZoneQueryParams(info.zoneId, FoldersDelta()), 'getZoneFolders')]
                yield zone
            yield zone
