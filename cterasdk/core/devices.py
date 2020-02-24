from .enum import DeviceType
from . import remote, query, union
from ..exception import CTERAException

name_attr = 'name'
type_attr = 'deviceType'
default = ['name', 'portal', 'deviceType']


def device(CTERAHost, device_name, include):
    include = union.union(include, default)
    include = ['/' + attr for attr in include]
    tenant = CTERAHost.session().tenant()
    url = '/portals/%s/devices/%s' % (tenant, device_name)

    dev = CTERAHost.get_multi(url, include)
    if dev.name is None:
        raise CTERAException('Device not found', None, tenant=tenant, device=device_name)

    return remote.remote_command(CTERAHost, dev)


def filers(CTERAHost, include, allPortals, deviceTypes):
    deviceTypes = [deviceType for deviceType in deviceTypes if deviceType in DeviceType.Gateways]
    if not deviceTypes:
        deviceTypes = DeviceType.Gateways

    filters = [query.FilterBuilder(type_attr).eq(deviceType) for deviceType in deviceTypes]
    return devices(CTERAHost, include, allPortals, filters)


def agents(CTERAHost, include, allPortals):
    filters = [query.FilterBuilder(type_attr).like('Agent')]
    return devices(CTERAHost, include, allPortals, filters)


def desktops(CTERAHost, include, allPortals):
    filters = [query.FilterBuilder(type_attr).eq(DeviceType.WorkstationAgent)]
    return devices(CTERAHost, include, allPortals, filters)


def servers(CTERAHost, include, allPortals):
    filters = [query.FilterBuilder(type_attr).eq(DeviceType.ServerAgent)]
    return devices(CTERAHost, include, allPortals, filters)


def by_name(CTERAHost, include, names):
    filters = [query.FilterBuilder('name').eq(name) for name in names]
    return devices(CTERAHost, include, False, filters)


def devices(CTERAHost, include, allPortals, filters):
    include = union.union(include, default)
    builder = query.QueryParamBuilder().include(include).allPortals(allPortals)
    for query_filter in filters:
        builder.addFilter(query_filter)
    builder.orFilter((len(filters) > 1))
    param = builder.build()

    # Check if the _all attribute conflicts with the current tenant
    iterator = CTERAHost.iterator('/devices', param)
    for dev in iterator:
        yield remote.remote_command(CTERAHost, dev)
