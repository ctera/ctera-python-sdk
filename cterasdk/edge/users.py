import logging

from ..common import Object
from ..exceptions import CTERAException
from .base_command import BaseCommand


class Users(BaseCommand):
    """ Edge Filer Users configuration APIs """

    def get(self, name=None):
        """
        Get User. If a user name was not passed as an argument, a list of all local users will be retrieved

        :param str,optional name: Name of the user
        """
        return self._edge.api.get('/config/auth/users' + ('' if name is None else ('/' + name)))

    def add_first_user(self, username, password, email=''):
        """
        Add the first user of the Edge Filer and login

        :param str username: User name for the new user
        :param str password: Password for the new user
        :param str,optional email: E-mail address of the new user, defaults to an empty string
        """
        if not self._edge.initialized:
            user = Object()
            user.username = username
            user.password = password
            user.email = email
            self._edge.api.post('/nosession/createfirstuser', user)
            logging.getLogger('cterasdk.edge').info('User created. %s', {'user': username})
        else:
            logging.getLogger('cterasdk.edge').info('Skipping. root account already exists.')
        self._edge.login(username, password)

    def add(self, username, password, full_name=None, email=None, uid=None):
        """
        Add a user of the Gateway

        :param str username: User name for the new user
        :param str password: Password for the new user
        :param str,optional full_name: The full name of the new user, defaults to None
        :param str,optional email: E-mail address of the new user, defaults to None
        :param str,optional uid: The uid of the new user, defaults to None
        """
        user = Object()
        user.username = username
        user.password = password
        user.fullName = full_name
        user.email = email
        user.uid = uid
        try:
            response = self._edge.api.add('/config/auth/users', user)
            logging.getLogger('cterasdk.edge').info("User created. %s", {'username': user.username})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.edge').error("User creation failed.")
            raise CTERAException('User creation failed', error)

    def modify(self, username, password=None, full_name=None, email=None, uid=None):
        """
        Modify an existing user of the Gateway

        :param str username: User name to modify
        :param str,optional password: New password, defaults to None
        :param str,optional full_name: The full name of the user, defaults to None
        :param str,optional email: E-mail address of the user, defaults to None
        :param str,optional uid: The uid of the user, defaults to None
        """
        try:
            user = self._edge.api.get('/config/auth/users/' + username)
        except CTERAException as error:
            raise CTERAException('Failed to get the user', error)

        if password:
            user.password = password
        if full_name:
            user.fullName = full_name
        if email:
            user.email = email
        if uid:
            user.uid = uid
        try:
            response = self._edge.api.put('/config/auth/users/' + username, user)
            logging.getLogger('cterasdk.edge').info("User modified. %s", {'username': user.username})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.edge').error("Failed to modify user.")
            raise CTERAException('Failed to modify user', error)

    def delete(self, username):
        """
        Delete an existing user

        :param str username: User name of the user to delete
        """
        try:
            response = self._edge.api.delete('/config/auth/users/' + username)
            logging.getLogger('cterasdk.edge').info("User deleted. %s", {'username': username})
            return response
        except Exception as error:
            logging.getLogger('cterasdk.edge').error("User deletion failed.")
            raise CTERAException('User deletion failed', error)
