import logging

from ..exception import CTERAException
from .base_command import BaseCommand


class Login(BaseCommand):

    def info(self):
        """
        Get login info
        """
        return self._gateway.get('/nosession/logininfo')

    def login(self, username, password):
        host = self._gateway.host()
        try:
            self._gateway.form_data('/login', {'username': username, 'password': password})
            logging.getLogger().info("User logged in. %s", {'host': host, 'user': username})
        except CTERAException as error:
            logging.getLogger().error("Login failed. %s", {'host': host, 'user': username})
            raise error

    def logout(self):
        host = self._gateway.host()
        user = self._gateway.session().user
        try:
            self._gateway.form_data('/logout', {'foo': 'bar'})
            logging.getLogger().info("User logged out. %s", {'host': self._gateway.host(), 'user': user})
        except CTERAException as error:
            logging.getLogger().error("Logout failed. %s", {'host': host, 'user': user})
            raise error
