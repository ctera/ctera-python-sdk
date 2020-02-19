from ..lib import Iterator, Command

from ..common import Object

from . import query

from datetime import datetime

def query_logs(ctera_host, param):
        
    response = ctera_host.execute('', 'queryLogs', param)

    return (response.hasMore, response.logs)

def logs(ctera_host, topic, minSeverity, originType, before, after):
    
    builder = query.QueryParamBuilder().put('topic', topic).put('minSeverity', minSeverity)
        
    if before != None:
        
        filter = query.FilterBuilder('time').before(strptime(before))
        
        builder.addFilter(filter)
        
    if after != None:
        
        filter = query.FilterBuilder('time').after(strptime(after))
        
        builder.addFilter(filter)
    
    param = builder.build()
    
    function = Command(query_logs, ctera_host)
    
    return Iterator(function, param)

def strptime(datetime_str):
    
    try:
        
        return datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
        
    except ValueError as error:
        
        raise error