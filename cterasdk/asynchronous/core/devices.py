from .base_command import BaseCommand
from . import remote
from ...core.query import QueryParamBuilder
from . import query
from ...common import union


class Devices(BaseCommand):
    """ Portal Devices APIs """

    async def devices(self, include=None, allPortals=False, filters=None, user=None):
        """
        Get Devices

        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']
        :param bool,optional allPortals: Search in all portals, defaults to False
        :param list[],optional filters: List of additional filters, defaults to None
        :param cterasdk.core.types.UserAccount user: User account of the device owner

        :return: Iterator for all matching Devices
        :rtype: cterasdk.lib.iterator.QueryIterator
        """
        include = union(include or [], ['name', 'portal', 'deviceType', 'version', 'remoteAccessUrl'])
        builder = QueryParamBuilder().include(include).allPortals(allPortals)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        if user:
            uid = self._core.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        builder.orFilter((len(filters) > 1))
        param = builder.build()

        iterator = query.iterator(self._core, '/devices', param)
        async for dev in iterator:
            yield remote.remote_command(self._core, dev)
