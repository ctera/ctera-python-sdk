import logging

from ..common import Object
from ..exception import CTERAException
from .base_command import BaseCommand


class Users(BaseCommand):

    def add_first_user(self, username, password, email=''):
        info = self._gateway.get('/nosession/logininfo')
        if info.isfirstlogin:
            user = Object()
            user.username = username
            user.password = password
            user.email = email
            self._gateway.post('/nosession/createfirstuser', user)
            logging.getLogger().info('User created. %s', {'user': username})
        else:
            logging.getLogger().info('Skipping. root account already exists.')
        self._gateway.login.login(username, password)

    def add(self, username, password, fullName=None, email=None, uid=None):
        user = Object()
        user.username = username
        user.password = password
        user.fullName = fullName
        user.email = email
        user.uid = uid
        try:
            response = self._gateway.add('/config/auth/users', user)
            logging.getLogger().info("User created. %s", {'username': user.username})
            return response
        except CTERAException as error:
            logging.getLogger().error("User creation failed.")
            raise CTERAException('User creation failed', error)

    def delete(self, username):
        try:
            response = self._gateway.delete('/config/auth/users/' + username)
            logging.getLogger().info("User deleted. %s", {'username': username})
            return response
        except Exception as error:
            logging.getLogger().error("User deletion failed.")
            raise CTERAException('User deletion failed', error)
