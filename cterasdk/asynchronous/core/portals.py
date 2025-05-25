from .base_command import BaseCommand
from ...core import decorator


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
