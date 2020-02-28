from .base_command import BaseCommand
from . import query
from . import union


class Servers(BaseCommand):
    """
    Global Admin Servers APIs
    """

    default = ['name']

    def list_servers(self, include=None):
        """
        Retrieve the servers that comprise CTERA Portal.\n
        To retrieve servers, you must first browse the Global Administration Portal, using: `GlobalAdmin.portals.browse_global_admin()`

        :param list[str],optional include: List of fields to retrieve, defaults to ['name']
        """
        # browse administration
        include = union.union(include or [], Servers.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._portal, '/servers', param)
