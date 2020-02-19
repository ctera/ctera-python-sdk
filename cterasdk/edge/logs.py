from ..lib import Command, Iterator

from ..common import Object

from . import query

import logging

def query_logs(ctera_host, param):
        
    response = ctera_host.execute('/config/logging/general', 'pagedQuery', param)

    return (response.hasMore, response.logs)

def logs(ctera_host, topic, include, minSeverity):
    
    param = query.QueryParamBuilder().include(include).put('topic', topic).put('minSeverity', minSeverity).build()
    
    function = Command(query_logs, ctera_host)
    
    return Iterator(function, param)