from .base_command import BaseCommand
from .enum import DeviceType
from . import remote, query, union
from ..exception import CTERAException


class Devices(BaseCommand):
    """ Portal Devices APIs """

    name_attr = 'name'
    type_attr = 'deviceType'
    default = ['name', 'portal', 'deviceType']

    def device(self, device_name, include=None):
        """
        Get a Device by its name

        :param str device_name: Name of the device to retrieve
        :param list[str],optional include: List of fields to retrieve, defaults to ['name', 'portal', 'deviceType']

        :return: Managed Device
        :rtype: ctera.object.Gateway.Gateway or ctera.object.Agent.Agent
        """
        include = union.union(include or [], Devices.default)
        include = ['/' + attr for attr in include]
        tenant = self._portal.session().tenant()
        url = '/portals/%s/devices/%s' % (tenant, device_name)

        dev = self._portal.get_multi(url, include)
        if dev.name is None:
            raise CTERAException('Device not found', None, tenant=tenant, device=device_name)

        return remote.remote_command(self._portal, dev)

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
        include = union.union(include or [], Devices.default)
        builder = query.QueryParamBuilder().include(include).allPortals(allPortals)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        if user:
            uid = self._portal.users.get(user, ['uid']).uid
            builder.ownedBy(uid)
        builder.orFilter((len(filters) > 1))
        param = builder.build()
        # Check if the _all attribute conflicts with the current tenant
        iterator = query.iterator(self._portal, '/devices', param)
        for dev in iterator:
            yield remote.remote_command(self._portal, dev)
