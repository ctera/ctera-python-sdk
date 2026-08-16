from .base_command import BaseCommand
from ...core import decorator
from ...core.query import QueryParamBuilder
from . import query


class Portals(BaseCommand):

    @decorator.update_current_tenant
    async def browse(self, tenant):
        """
        Browse a tenant

        :param str tenant: Name of the tenant to browse
        """
        await self._core.v1.api.put('/currentPortal', tenant)

    async def browse_global_admin(self):
        """
        Browse the Global Admin
        """
        await self.browse('')

    def tenants(self, include_deleted=False):
        """
        Get all tenants

        :param bool,optional include_deleted: Include deleted tenants, defaults to False
        """
        param = QueryParamBuilder().include_classname().put('isTrashcan', include_deleted).build()
        return query.iterator(self._core, '', param, 'getPortalsDisplayInfo')
