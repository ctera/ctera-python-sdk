import logging
import asyncio

from ...common import union
from .base_command import BaseCommand
from ...core.query import QueryParamBuilder
from . import query


logger = logging.getLogger('cterasdk.core')


class Servers(BaseCommand):
    """
    Global Admin Servers APIs
    """

    default = ['name']

    async def system_info(self, server):
        return await self._core.v1.api.get(f'/servers/{server.name}/systemInfo')

    async def list_servers(self, include=None):
        """
        Retrieve the servers that comprise CTERA Portal.
        Restricted to the Global Administration Portal. Browse it using :py:func:`cterasdk.core.portals.browse_global_admin`.

        :param list[str],optional include: List of fields to retrieve, defaults to ['name']
        """
        include = union(include or [], Servers.default)
        param = QueryParamBuilder().include(include).build()

        servers = [server async for server in query.iterator(self._core, '/servers', param)]

        if 'systemInfo' in include:
            tasks = [self.system_info(server) for server in servers]
            systems = await asyncio.gather(*tasks)

            for server, sys_info in zip(servers, systems):
                server.systemInfo = sys_info

        for server in servers:
            yield server
