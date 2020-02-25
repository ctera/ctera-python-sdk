import logging

from .base_command import BaseCommand
from ..common import Object
from . import query
from . import union


class Users(BaseCommand):

    default = ['name']

    def local_users(self, include=None):
        include = union.union(include or [], Users.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._portal, '/users', param)

    def domains(self):
        return self._portal.get('/domains')

    def domain_users(self, domain, include=None):
        include = union.union(include or [], Users.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._portal, '/domains/' + domain + '/adUsers', param)

    def add(self, name, email, first_name, last_name, password, role, company=None, comment=None):
        param = Object()
        param._classname = "PortalUser"  # pylint: disable=protected-access
        param.name = name
        param.email = email
        param.firstName = first_name
        param.lastName = last_name
        param.password = password
        param.role = role
        param.company = company
        param.comment = comment

        logging.getLogger().info('Creating user. %s', {'user': name})

        response = self._portal.add('/users', param)

        logging.getLogger().info('User created. %s', {'user': name, 'email': email, 'role': role})

        return response

    def delete(self, name):
        logging.getLogger().info('Deleting user. %s', {'user': name})

        response = self._portal.execute('/users/' + name, 'delete', True)

        logging.getLogger().info('User deleted. %s', {'user': name})

        return response
