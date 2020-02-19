from ..common import Object

from . import query

from . import union

import logging

default = ['name']

def local_users(CTERAHost, include):
    
    include = union.union(include, default)
    
    param = query.QueryParamBuilder().include(include).build()
    
    return CTERAHost.iterator('/users', param)

def domain_users(CTERAHost, include):
    
    include = union.union(include, default)
    
    param = query.QueryParamBuilder().include(include).build()
    
    return CTERAHost.iterator('/domains/' + domain + '/adUsers', param)

def add(ctera_host, name, email, first_name, last_name, password, role, company, comment):

    param = Object()
    
    param._classname = "PortalUser"

    param.name = name
    
    param.email = email

    param.firstName = first_name

    param.lastName = last_name
    
    param.password = password
    
    param.role = role
    
    param.company = company
    
    param.comment = comment
    
    logging.getLogger().info('Creating user. {0}'.format({'user' : name}))

    response = ctera_host.add('/users', param)
    
    logging.getLogger().info('User created. {0}'.format({'user' : name, 'email' : email, 'role' : role}))
    
    return response

def delete(ctera_host, name):
    
    logging.getLogger().info('Deleting user. {0}'.format({'user' : name}))
    
    response = ctera_host.execute('/users/' + name, 'delete', True)
    
    logging.getLogger().info('User deleted. {0}'.format({'user' : name}))
    
    return response
    
    