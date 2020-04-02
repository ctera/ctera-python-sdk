import logging

from .base_command import BaseCommand
from ..lib import Iterator, Command
from ..common import Object
from . import query


class Portals(BaseCommand):
    """
    Global Admin Portals APIs
    """
    def _query_portals(self, param):
        response = self._portal.execute('', 'getPortalsDisplayInfo', param)
        return (response.hasMore, response.objects)

    def tenants(self, include_deleted=False):
        """
        Get all tenants

        :param bool,optional include_deleted: Include deleted tenants, defaults to False
        """
        # Check if current session is global admin
        param = query.QueryParamBuilder().include_classname().put('isTrashcan', include_deleted).build()
        function = Command(self._query_portals)
        return Iterator(function, param)

    def add(self, name, display_name=None, billing_id=None, company=None):
        """
        Add a new tenant

        :param str name: Name of the new tenant
        :param str,optional display_name: Display Name of the new tenant, defaults to None
        :param str,optional billing_id: Billing ID of the new tenant, defaults to None
        :param str,optional company: Company Name of the new tenant, defaults to None
        :return str: A relative url path to the Team Portal
        """
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
        """
        Delete an existing tenant

        :param str name: Name of the tenant to delete
        """
        logging.getLogger().info('Deleting Portal. %s', {'name': name})

        response = self._portal.execute('/teamPortals/' + name, 'delete')

        logging.getLogger().info('Portal deleted. %s', {'name': name})

        return response

    def undelete(self, name):
        """
        Undelete a previously deleted tenant

        :param str name: Name of the tenant to undelete
        """
        logging.getLogger().info('Recovering Portal. %s', {'name': name})

        response = self._portal.execute('/teamPortals/' + name, 'moveFromTrashcan')

        logging.getLogger().info('Portal recovered. %s', {'name': name})

        return response

    def browse(self, tenant):
        """
        Browse a tenant

        :param str tenant: Name of the tenant to browse
        """
        self._portal.put('/currentPortal', tenant)

    def browse_global_admin(self):
        """
        Browse the Global Admin
        """
        self.browse('')
