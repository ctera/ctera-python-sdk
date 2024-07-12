from .base_command import BaseCommand
from .enum import DeviceType
from . import remote, query
from ..common import union
from ..exceptions import CTERAException, ObjectNotFoundException


class Devices(BaseCommand):
    """ Portal Devices APIs """

    name_attr = 'name'
    type_attr = 'deviceType'
    default = ['name', 'portal', 'deviceType', 'version', 'remoteAccessUrl']

    def _create_device_resource_uri(self, device_name, tenant):
        session = self._core.session()
        if not tenant:
            if not session.in_tenant_context():
                raise CTERAException('You must specify a tenant name or browse the tenant first.')
            tenant = self._core.session().current_tenant()
        resource_uri = f'/portals/{tenant}/devices/{device_name}'  # regular auth: support both tenant and Administration context
        return resource_uri

    def device(self, device_name, tenant=None, include=None):
        """
        Get a Device by its name

        :param str device_name: Name of the device to retrieve
        :param str,optional tenant: Tenant of the device, defaults to the tenant in the current session
        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']

        :return: Managed Device
        :rtype: cterasdk.objects.synchronous.Edge or cterasdk.objects.synchronous.Drive
        """
        include = union(include or [], Devices.default)
        include = ['/' + attr for attr in include]

        resource_uri = self._create_device_resource_uri(device_name, tenant)

        dev = self._core.api.get_multi(resource_uri, include)
        if dev.name is None:
            raise ObjectNotFoundException('Device not found', resource_uri, tenant=tenant, name=device_name)

        return remote.remote_command(self._core, dev)

    def filers(self, include=None, allPortals=False, deviceTypes=None):
        """
        Get Filers

        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']
        :param bool,optional allPortals: Search in all portals, defaults to False
        :param list[cterasdk.core.enum.DeviceType.Gateways] deviceTypes: Types of Filers, defaults to all Filer types

        :return: Iterator for all matching Filers
        :rtype: cterasdk.lib.iterator.Iterator[cterasdk.object.Gateway.Gateway]
        """
        if deviceTypes:
            deviceTypes = [deviceType for deviceType in deviceTypes if deviceType in DeviceType.Gateways]
        if not deviceTypes:
            deviceTypes = DeviceType.Gateways

        filters = [query.FilterBuilder(Devices.type_attr).eq(deviceType) for deviceType in deviceTypes]
        return self.devices(include, allPortals, filters)

    def agents(self, include=None, allPortals=False):
        """
        Get Agents

        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']
        :param bool,optional allPortals: Search in all portals, defaults to False

        :return: Iterator for all matching Agents
        :rtype: cterasdk.lib.iterator.Iterator[cterasdk.object.Agent.Agent]
        """
        filters = [query.FilterBuilder(Devices.type_attr).like('Agent')]
        return self.devices(include, allPortals, filters)

    def desktops(self, include=None, allPortals=False):
        """
        Get Desktops

        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']
        :param bool,optional allPortals: Search in all portals, defaults to False

        :return: Iterator for all matching Desktops
        :rtype: cterasdk.lib.iterator.Iterator
        """
        filters = [query.FilterBuilder(Devices.type_attr).eq(DeviceType.WorkstationAgent)]
        return self.devices(include, allPortals, filters)

    def servers(self, include=None, allPortals=False):
        """
        Get Servers

        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']
        :param bool,optional allPortals: Search in all portals, defaults to False

        :return: Iterator for all matching Servers
        :rtype: cterasdk.lib.iterator.Iterator
        """
        filters = [query.FilterBuilder(Devices.type_attr).eq(DeviceType.ServerAgent)]
        return self.devices(include, allPortals, filters)

    def by_name(self, names, include=None):
        """
        Get Devices by their names

        :param list[str],optional names: List of names of devices
        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']

        :return: Iterator for all matching Devices
        :rtype: cterasdk.lib.iterator.Iterator
        """
        filters = [query.FilterBuilder('name').eq(name) for name in names]
        return self.devices(include, False, filters)

    def devices(self, include=None, allPortals=False, filters=None, user=None):
        """
        Get Devices

        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']
        :param bool,optional allPortals: Search in all portals, defaults to False
        :param list[],optional filters: List of additional filters, defaults to None
        :param cterasdk.core.types.UserAccount user: User account of the device owner

        :return: Iterator for all matching Devices
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union(include or [], Devices.default)
        builder = query.QueryParamBuilder().include(include).allPortals(allPortals)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        if user:
            uid = self._core.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        builder.orFilter((len(filters) > 1))
        param = builder.build()
        # Check if the _all attribute conflicts with the current tenant
        iterator = query.iterator(self._core, '/devices', param)
        for dev in iterator:
            yield remote.remote_command(self._core, dev)

    def get_comment(self, device_name, tenant=None):
        """
        Get Portal device comment

        :param str device: Device name
        :returns: Comment
        :rtype: str
        """
        return self._core.api.get(f'{self._create_device_resource_uri(device_name, tenant)}/comment')

    def set_comment(self, device_name, comment, tenant=None):
        """
        Set a comment to a Portal device

        :param str device: Device name
        :param str comment: Comment
        """
        return self._core.api.put(f'{self._create_device_resource_uri(device_name, tenant)}/comment', comment)
