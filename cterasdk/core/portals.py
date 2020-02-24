import logging

from ..lib import Iterator, Command
from ..common import Object
from . import query


def query_portals(ctera_host, param):
    response = ctera_host.execute('', 'getPortalsDisplayInfo', param)
    return (response.hasMore, response.objects)


def portals(ctera_host, include_deleted=False):
    # Check if current session is global admin
    param = query.QueryParamBuilder().include_classname().put('isTrashcan', include_deleted).build()
    function = Command(query_portals, ctera_host)
    return Iterator(function, param)


def add(ctera_host, name, display_name, billing_id, company):
    param = Object()
    param._classname = 'TeamPortal'  # pylint: disable=protected-access
    param.name = name
    param.displayName = display_name
    param.externalPortalId = billing_id
    param.companyName = company

    ctera_host.browse_global_admin()

    logging.getLogger().info('Creating Team Portal. %s', {'name': name})

    response = ctera_host.add('/teamPortals', param)

    logging.getLogger().info('Team Portal created. %s', {'name': name})

    return response


def delete(ctera_host, name):
    logging.getLogger().info('Deleting Portal. %s', {'name': name})

    response = ctera_host.execute('/teamPortals/' + name, 'delete')

    logging.getLogger().info('Portal deleted. %s', {'name': name})

    return response


def undelete(ctera_host, name):
    logging.getLogger().info('Recovering Portal. %s', {'name': name})

    response = ctera_host.execute('/teamPortals/' + name, 'moveFromTrashcan')

    logging.getLogger().info('Portal recovered. %s', {'name': name})

    return response


def browse(ctera_host, tenant):
    ctera_host.put('/currentPortal', tenant)
