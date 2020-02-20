from datetime import datetime

from ..lib import Iterator, Command
from . import query


def query_logs(ctera_host, param):
    response = ctera_host.execute('', 'queryLogs', param)
    return (response.hasMore, response.logs)

def logs(ctera_host, topic, minSeverity, _originType, before, after):
    builder = query.QueryParamBuilder().put('topic', topic).put('minSeverity', minSeverity)

    if before is not None:
        builder.addFilter(query.FilterBuilder('time').before(strptime(before)))

    if after is not None:
        builder.addFilter(query.FilterBuilder('time').after(strptime(after)))

    param = builder.build()
    function = Command(query_logs, ctera_host)

    return Iterator(function, param)

def strptime(datetime_str):
    try:
        return datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
    except ValueError as error:
        raise error
