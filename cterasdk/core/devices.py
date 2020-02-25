from .base_command import BaseCommand
from .enum import DeviceType
from . import remote, query, union
from ..exception import CTERAException


class Devices(BaseCommand):

    name_attr = 'name'
    type_attr = 'deviceType'
    default = ['name', 'portal', 'deviceType']

    def device(self, device_name, include=None):
        include = union.union(include or [], Devices.default)
        include = ['/' + attr for attr in include]
        tenant = self._portal.session().tenant()
        url = '/portals/%s/devices/%s' % (tenant, device_name)

        dev = self._portal.get_multi(url, include)
        if dev.name is None:
            raise CTERAException('Device not found', None, tenant=tenant, device=device_name)

        return remote.remote_command(self._portal, dev)

    def filers(self, include=None, allPortals=False, deviceTypes=None):
        if deviceTypes:
            deviceTypes = [deviceType for deviceType in deviceTypes if deviceType in DeviceType.Gateways]
        if not deviceTypes:
            deviceTypes = DeviceType.Gateways

        filters = [query.FilterBuilder(Devices.type_attr).eq(deviceType) for deviceType in deviceTypes]
        return self.devices(include, allPortals, filters)

    def agents(self, include=None, allPortals=False):
        filters = [query.FilterBuilder(Devices.type_attr).like('Agent')]
        return self.devices(include, allPortals, filters)

    def desktops(self, include=None, allPortals=False):
        filters = [query.FilterBuilder(Devices.type_attr).eq(DeviceType.WorkstationAgent)]
        return self.devices(include, allPortals, filters)

    def servers(self, include=None, allPortals=False):
        filters = [query.FilterBuilder(Devices.type_attr).eq(DeviceType.ServerAgent)]
        return self.devices(include, allPortals, filters)

    def by_name(self, names, include=None):
        filters = [query.FilterBuilder('name').eq(name) for name in names]
        return self.devices(include, False, filters)

    def devices(self, include=None, allPortals=False, filters=None):
        include = union.union(include or [], Devices.default)
        builder = query.QueryParamBuilder().include(include).allPortals(allPortals)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        builder.orFilter((len(filters) > 1))
        param = builder.build()

        # Check if the _all attribute conflicts with the current tenant
        iterator = query.iterator(self._portal, '/devices', param)
        for dev in iterator:
            yield remote.remote_command(self._portal, dev)
