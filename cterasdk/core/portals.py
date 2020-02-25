import logging

from .base_command import BaseCommand
from ..lib import Iterator, Command
from ..common import Object
from . import query


class Portals(BaseCommand):
    def query_portals(self, param):
        response = self._portal.execute('', 'getPortalsDisplayInfo', param)
        return (response.hasMore, response.objects)

    def tenants(self, include_deleted=False):
        # Check if current session is global admin
        param = query.QueryParamBuilder().include_classname().put('isTrashcan', include_deleted).build()
        function = Command(self.query_portals)
        return Iterator(function, param)

    def add(self, name, display_name=None, billing_id=None, company=None):
        param = Object()
        param._classname = 'TeamPortal'  # pylint: disable=protected-access
        param.name = name
        param.displayName = display_name
        param.externalPortalId = billing_id
        param.companyName = company

        logging.getLogger().info('Creating Team Portal. %s', {'name': name})

        response = self._portal.add('/teamPortals', param)

        logging.getLogger().info('Team Portal created. %s', {'name': name})

        return response

    def delete(self, name):
        logging.getLogger().info('Deleting Portal. %s', {'name': name})

        response = self._portal.execute('/teamPortals/' + name, 'delete')

        logging.getLogger().info('Portal deleted. %s', {'name': name})

        return response

    def undelete(self, name):
        logging.getLogger().info('Recovering Portal. %s', {'name': name})

        response = self._portal.execute('/teamPortals/' + name, 'moveFromTrashcan')

        logging.getLogger().info('Portal recovered. %s', {'name': name})

        return response

    def browse(self, tenant):
        self._portal.put('/currentPortal', tenant)

    def browse_global_admin(self):
        self.browse('')
