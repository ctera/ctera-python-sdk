from .enum import DeviceType

from ..lib import Iterator, Command

from . import remote, query, union

from ..exception import CTERAException

import logging

name_attr = 'name'

type_attr = 'deviceType'

default = ['name', 'portal', 'deviceType']

def device(CTERAHost, device_name, include):
    
    include = union.union(include, default)
    
    include = ['/' + attr for attr in include]
    
    tenant = CTERAHost.session().tenant()
    
    url = '/portals/%s/devices/%s' % (tenant, device_name)
    
    device = CTERAHost.get_multi(url, include)
    
    if device.name == None:
        
        raise CTERAException('Device not found', None, tenant = tenant, device = device_name)
    
    return remote.remote_command(CTERAHost, device)

def filers(CTERAHost, include, allPortals, deviceTypes):
    
    deviceTypes = [deviceType for deviceType in deviceTypes if deviceType in DeviceType.Gateways]
    
    if not deviceTypes:
        
        deviceTypes = DeviceType.Gateways
    
    filters = []
    
    for deviceType in deviceTypes:
        
        filter = query.FilterBuilder(type_attr).eq(deviceType)
        
        filters.append(filter)
        
    return devices(CTERAHost, include, allPortals, filters)
        
def agents(CTERAHost, include, allPortals):
    
    filters = [ query.FilterBuilder(type_attr).like('Agent') ]
    
    return devices(CTERAHost, include, allPortals, filters)

def desktops(CTERAHost, include, allPortals):
    
    filters = [ query.FilterBuilder(type_attr).eq(DeviceType.WorkstationAgent) ]
    
    return devices(CTERAHost, include, allPortals, filters)

def servers(CTERAHost, include, allPortals):
    
    filters = [ query.FilterBuilder(type_attr).eq(DeviceType.ServerAgent) ]
    
    return devices(CTERAHost, include, allPortals, filters)

def by_name(CTERAHost, include, names):
    
    filters = []
    
    for name in names:
        
        qf = query.FilterBuilder('name').eq(name)
        
        filters.append(qf)
        
    return devices(CTERAHost, include, False, filters)
    
def devices(CTERAHost, include, allPortals, filters):
    
    include = union.union(include, default)
    
    builder = query.QueryParamBuilder().include(include).allPortals(allPortals)
    
    for filter in filters:
        
        builder.addFilter(filter)
        
    builder.orFilter( ( len(filters) > 1 ) )
    
    param = builder.build()
    
    # Check if the _all attribute conflicts with the current tenant
    
    iterator = CTERAHost.iterator('/devices', param)
    
    for device in iterator:
        
        yield remote.remote_command(CTERAHost, device)