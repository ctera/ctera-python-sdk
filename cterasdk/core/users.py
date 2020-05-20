import logging

from .base_command import BaseCommand
from ..exception import CTERAException
from ..common import Object, DateTimeUtils
from . import query
from . import union


class Users(BaseCommand):
    """
    Portal User Management APIs
    """

    default = ['name']

    def get(self, user_account, include=None):
        """
        Get a user account

        :param cterasdk.core.types.UserAccount user_account: User account, including the user directory and user name
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: The user account, including the requested fields
        """
        baseurl = '/users/%s' % user_account.name if user_account.is_local \
            else '/domains/%s/adUsers/%s' % (user_account.directory, user_account.name)
        include = union.union(include or [], Users.default)
        include = ['/' + attr for attr in include]
        user_object = self._portal.get_multi(baseurl, include)
        if user_object.name is None:
            raise CTERAException('Could not find user', None, user_directory=user_account.directory, username=user_account.name)
        return user_object

    def list_local_users(self, include=None):
        """
        List all local users

        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: Iterator for all local users
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union.union(include or [], Users.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._portal, '/users', param)

    def list_domains(self):
        """
        List all domains

        :return list: List of all domains
        """
        return self._portal.get('/domains')

    def list_domain_users(self, domain, include=None):
        """
        List all the users in the domain

        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: Iterator for all the domain users
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union.union(include or [], Users.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._portal, '/domains/' + domain + '/adUsers', param)

    def add(self, name, email, first_name, last_name, password, role, company=None, comment=None, password_change=False):
        """
        Add a portal user

        :param str name: User name for the new user
        :param str email: E-mail address of the new user
        :param str first_name: The first name of the new user
        :param str last_name: The last name of the new user
        :param str password: Password for the new user
        :param cterasdk.core.enum.Role role: User role of the new user
        :param str,optional company: The name of the company of the new user, defaults to None
        :param str,optional comment: Additional comment for the new user, defaults to None
        :param variable,optional password_change:
            Require the user to change the password on the first login.
            Pass datetime.date for a specific date, integer for days from creation, or True for immediate , defaults to False
        """
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
        if password_change:
            param.requirePasswordChangeOn = DateTimeUtils.get_expiration_date(password_change).strftime('%Y-%m-%d')

        logging.getLogger().info('Creating user. %s', {'user': name})
        response = self._portal.add('/users', param)
        logging.getLogger().info('User created. %s', {'user': name, 'email': email, 'role': role})

        return response

    def delete(self, user):
        """
        Delete a user

        :param cterasdk.core.types.UserAccount user: the user account
        """
        logging.getLogger().info('Deleting user. %s', {'user': str(user)})
        baseurl = '/users/%s' % user.name if user.is_local else '/domains/%s/adUsers/%s' % (user.directory, user.name)
        response = self._portal.execute(baseurl, 'delete', True)
        logging.getLogger().info('User deleted. %s', {'user': str(user)})

        return response
