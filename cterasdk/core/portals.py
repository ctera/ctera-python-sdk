import logging

from ..exceptions import ObjectNotFoundException
from .base_command import BaseCommand
from ..common import Object, union
from . import enum, query, decorator


class Portals(BaseCommand):
    """
    Global Admin Portals APIs
    """

    default = ['name']

    def get(self, name, include=None):
        """
        Get a tenant

        :param str name: Name of the tenant
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        """
        include = union(include or [], Portals.default)
        include = ['/' + attr for attr in include]
        tenant = self._core.api.get_multi('/portals/' + name, include)
        if tenant.name is None:
            raise ObjectNotFoundException('Could not find tenant', f'/portals/{name}', name=name)
        return tenant

    def list_tenants(self, include=None, portal_type=None):
        """
        List tenants.\n
        To retrieve tenants, you must first browse the Global Administration Portal, using: `GlobalAdmin.portals.browse_global_admin()`

        :param list[str],optional include: List of fields to retrieve, defaults to ['name']
        :param cterasdk.core.enum.PortalType portal_type: The Portal type
        """
        # browse administration
        include = union(include or [], Portals.default)
        param = query.QueryParamBuilder().include(include).build()
        baseurl = '/portals'
        if portal_type == enum.PortalType.Team:
            baseurl = '/teamPortals'
        elif portal_type == enum.PortalType.Reseller:
            baseurl = '/resellerPortals'
        return query.iterator(self._core, baseurl, param)

    def tenants(self, include_deleted=False):
        """
        Get all tenants

        :param bool,optional include_deleted: Include deleted tenants, defaults to False
        """
        # Check if current session is global admin
        param = query.QueryParamBuilder().include_classname().put('isTrashcan', include_deleted).build()
        return query.iterator(self._core, '', param, 'getPortalsDisplayInfo')

    def add(self, name, display_name=None, billing_id=None, company=None, plan=None, comment=None):
        """
        Add a new tenant

        :param str name: Name of the new tenant
        :param str,optional display_name: Display Name of the new tenant, defaults to None
        :param str,optional billing_id: Billing ID of the new tenant, defaults to None
        :param str,optional company: Company Name of the new tenant, defaults to None
        :param str,optional plan: Subscription plan name to assign to the new tenant, defaults to None
        :param str,optional comment: Assign a comment to the new tenant, defaults to None
        :return str: A relative url path to the Team Portal
        """

        param = Object()
        if plan:
            param.plan = self._core.plans.get(plan, include=['baseObjectRef']).baseObjectRef
        param._classname = 'TeamPortal'  # pylint: disable=protected-access
        param.name = name
        param.displayName = display_name
        param.externalPortalId = billing_id
        param.companyName = company
        param.comment = comment

        logging.getLogger('cterasdk.core').info('Creating Team Portal. %s', {'name': name})

        response = self._core.api.add('/teamPortals', param)

        logging.getLogger('cterasdk.core').info('Team Portal created. %s', {'name': name})

        return response

    def subscribe(self, tenant, plan):
        """
        Subscribe a tenant to a plan

        :param str name: Name of the tenant
        :param str,plan: Name of the subscription plan
        """
        return self._core.api.execute('/portals/' + tenant, 'subscribe', plan)

    def delete(self, name):
        """
        Delete an existing tenant

        :param str name: Name of the tenant to delete
        """
        logging.getLogger('cterasdk.core').info('Deleting Portal. %s', {'name': name})

        response = self._core.api.execute('/teamPortals/' + name, 'delete')

        logging.getLogger('cterasdk.core').info('Portal deleted. %s', {'name': name})

        return response

    def undelete(self, name):
        """
        Undelete a previously deleted tenant

        :param str name: Name of the tenant to undelete
        """
        logging.getLogger('cterasdk.core').info('Recovering Portal. %s', {'name': name})

        response = self._core.api.execute('/teamPortals/' + name, 'moveFromTrashcan')

        logging.getLogger('cterasdk.core').info('Portal recovered. %s', {'name': name})

        return response

    @decorator.update_current_tenant
    def browse(self, tenant):
        """
        Browse a tenant

        :param str tenant: Name of the tenant to browse
        """
        self._core.api.put('/currentPortal', tenant)

    def browse_global_admin(self):
        """
        Browse the Global Admin
        """
        self.browse('')

    def apply_changes(self, wait=False):
        """
        Apply provisioning changes.\n

        :param bool,optional wait: Wait for all changes to apply
        """
        param = Object()
        param.objectId = None
        param.type = 'portals'
        logging.getLogger('cterasdk.core').info('Applying provisioning changes.')
        task = self._core.api.execute('', 'updatePortals', param)
        if wait:
            task = self._core.tasks.wait(task)
        return task
