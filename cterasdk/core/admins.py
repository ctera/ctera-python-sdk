import logging

from .base_command import BaseCommand
from ..exceptions import CTERAException, ObjectNotFoundException
from ..common import Object, DateTimeUtils
from ..common import union
from . import query


class Administrators(BaseCommand):
    """
    Portal Global Administrators User Management APIs
    """

    default = ['name']

    def _get_entire_object(self, name):
        ref = f'/administrators/{name}'
        try:
            return self._core.api.get(ref)
        except CTERAException as error:
            raise CTERAException('Failed to get the user', error)

    def get(self, name, include=None):
        """
        Get a Global Administrator user account

        :param str name: Global administrator username
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: The user account, including the requested fields
        """
        baseurl = f'/administrators/{name}'
        include = union(include or [], Administrators.default)
        include = ['/' + attr for attr in include]
        user_object = self._core.api.get_multi(baseurl, include)
        if user_object.name is None:
            raise ObjectNotFoundException('Could not find user', baseurl, username=name)
        return user_object

    def list_admins(self, include=None):
        """
        List local administrators

        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: Iterator for local administrators
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union(include or [], Administrators.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._core, '/administrators', param)

    def add(self, name, email, first_name, last_name, password, role, company=None, comment=None, password_change=False):
        """
        Create a Global Administrator

        :param str name: User name for the new GlobalAdmin
        :param str email: E-mail address of the new GlobalAdmin
        :param str first_name: The first name of the new GlobalAdmin
        :param str last_name: The last name of the new GlobalAdmin
        :param str password: Password for the new GlobalAdmin
        :param cterasdk.core.enum.Role role: User role of the new GlobalAdmin
        :param str,optional company: The name of the company of the new GlobalAdmin, defaults to None
        :param str,optional comment: Additional comment for the new GlobalAdmin, defaults to None
        :param variable,optional password_change:
            Require the user to change the password on the first login.
            Pass datetime.date for a specific date, integer for days from creation, or True for immediate , defaults to False
        """
        param = Object()
        param._classname = "PortalAdmin"  # pylint: disable=protected-access
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

        logging.getLogger('cterasdk.core').info('Creating a global administrator. %s', {'user': name})
        response = self._core.api.add('/administrators', param)
        logging.getLogger('cterasdk.core').info('Global administrator created. %s', {'user': name, 'email': email, 'role': role})

        return response

    def modify(self, current_username, new_username=None, email=None, first_name=None,
               last_name=None, password=None, role=None, company=None, comment=None):
        """
        Modify a Global Administrator user account

        :param str current_username: The current GlobalAdmin username
        :param str,optional new_username: New name
        :param str,optional email: E-mail address
        :param str,optional first_name: First name
        :param str,optional last_name: Last name
        :param str,optional password: Password
        :param cterasdk.core.enum.Role,optional role: User role
        :param str,optional company: Company name
        :param str,optional comment: Comment
        """
        user = self._get_entire_object(current_username)
        if new_username:
            user.name = new_username
        if email:
            user.email = email
        if first_name:
            user.firstName = first_name
        if last_name:
            user.lastName = last_name
        if password:
            user.password = password
        if role:
            user.role = role
        if company is not None:
            user.company = company
        if comment is not None:
            user.comment = comment

        try:
            response = self._core.api.put('/administrators/' + current_username, user)
            logging.getLogger('cterasdk.core').info("User modified. %s", {'username': user.name})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.core').error("Failed to modify user.")
            raise CTERAException('Failed to modify user', error)

    def delete(self, name):
        """
        Delete a Global Administrator

        :param str username: Global administrator username
        """
        logging.getLogger('cterasdk.core').info('Deleting user. %s', {'user': name})
        baseurl = f'/administrators/{name}'
        response = self._core.api.execute(baseurl, 'delete', True)
        logging.getLogger('cterasdk.core').info('User deleted. %s', {'user': name})

        return response
