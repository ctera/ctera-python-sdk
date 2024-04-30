import logging

from .base_command import BaseCommand
from .types import UserAccount
from ..exceptions import CTERAException, ObjectNotFoundException
from ..common import Object, DateTimeUtils
from ..common import union
from . import query


class Users(BaseCommand):
    """
    Portal User Management APIs

    :ivar cterasdk.core.credentials.Credentials credentials: Object holding Portal User Credential Management APIs.
    """

    default = ['name']

    def __init__(self, portal):
        super().__init__(portal)
        self.credentials = Credentials(self._core)

    def _get_entire_object(self, user_account):
        ref = f'/users/{user_account.name}' if user_account.is_local \
            else f'/domains/{user_account.directory}/adUsers/{user_account.name}'
        try:
            return self._core.api.get(ref)
        except CTERAException as error:
            raise CTERAException('Failed to get the user', error)

    def get(self, user_account, include=None):
        """
        Get a user account

        :param cterasdk.core.types.UserAccount user_account: User account, including the user directory and user name
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: The user account, including the requested fields
        """
        baseurl = f'/users/{user_account.name}' if user_account.is_local \
            else f'/domains/{user_account.directory}/adUsers/{user_account.name}'
        include = union(include or [], Users.default)
        include = ['/' + attr for attr in include]
        user_object = self._core.api.get_multi(baseurl, include)
        if user_object.name is None:
            raise ObjectNotFoundException('Could not find user', baseurl, user_directory=user_account.directory, username=user_account.name)
        return user_object

    def list_local_users(self, include=None):
        """
        List all local users

        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: Iterator for all local users
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union(include or [], Users.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._core, '/users', param)

    def list_domain_users(self, domain, include=None):
        """
        List all the users in the domain

        :param str domain: Domain name
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: Iterator for all the domain users
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union(include or [], Users.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._core, f'/domains/{domain}/adUsers', param)

    def add(self, name, email, first_name, last_name, password, role, company=None, comment=None, password_change=False):
        """
        Create a local user account

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

        logging.getLogger('cterasdk.core').info('Creating user. %s', {'user': name})
        response = self._core.api.add('/users', param)
        logging.getLogger('cterasdk.core').info('User created. %s', {'user': name, 'email': email, 'role': role})

        return response

    def modify(self, current_username, new_username=None, email=None, first_name=None,
               last_name=None, password=None, role=None, company=None, comment=None):
        """
        Modify a local user account

        :param str current_username: The current user name
        :param str,optional new_username: New name
        :param str,optional email: E-mail address
        :param str,optional first_name: First name
        :param str,optional last_name: Last name
        :param str,optional password: Password
        :param cterasdk.core.enum.Role,optional role: User role
        :param str,optional company: Company name
        :param str,optional comment: Comment
        """
        user_account = UserAccount(current_username)
        user = self._get_entire_object(user_account)
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
            response = self._core.api.put('/users/' + current_username, user)
            logging.getLogger('cterasdk.core').info("User modified. %s", {'username': user.name})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.core').error("Failed to modify user.")
            raise CTERAException('Failed to modify user', error)

    def apply_changes(self, wait=False):
        """
        Apply provisioning changes.\n

        :param bool,optional wait: Wait for all changes to apply
        """
        param = Object()
        param.objectId = None
        param.type = 'users'
        logging.getLogger('cterasdk.core').info('Applying provisioning changes.')
        task = self._core.api.execute('', 'updateAccounts', param)
        if wait:
            task = self._core.tasks.wait(task)
        return task

    def delete(self, user):
        """
        Delete a user

        :param cterasdk.core.types.UserAccount user: the user account
        """
        logging.getLogger('cterasdk.core').info('Deleting user. %s', {'user': str(user)})
        baseurl = f'/users/{user.name}' if user.is_local else f'/domains/{user.directory}/adUsers/{user.name}'
        response = self._core.api.execute(baseurl, 'delete', True)
        logging.getLogger('cterasdk.core').info('User deleted. %s', {'user': str(user)})

        return response


class Credentials(BaseCommand):
    """
    Portal Credential Management APIs

    :ivar cterasdk.core.credentials.S3 s3: Object holding the Portal User S3 Credential Management APIs.
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.s3 = S3(self._core)


class S3(BaseCommand):
    """
    S3 Credential Management APIs
    """

    def all(self, user_account):
        """
        List Credentials

        :param cterasdk.core.types.UserAccount user_account: User account
        """
        return self._core.credentials.s3.all(user_account)

    def create(self, user_account):
        """
        Create Credential

        :param cterasdk.core.types.UserAccount user_account: User account
        """
        return self._core.credentials.s3.create(user_account)

    def delete(self, access_key_id, user_account):
        """
        Delete Credential

        :param str access_key_id: Access Key ID
        :param cterasdk.core.types.UserAccount user_account: User account
        """
        return self._core.credentials.s3.delete(access_key_id, user_account)
