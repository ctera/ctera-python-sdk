from ..common import Object

from . import query

from . import union

default = ['name']

def servers(CTERAHost, include):
    
    # browse administration
    
    include = union.union(include, default)
    
    param = query.QueryParamBuilder().include(include).build()
    
    return CTERAHost.iterator('/servers', param)