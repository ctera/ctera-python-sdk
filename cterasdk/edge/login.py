import logging

from ..exception import CTERAException
from .base_command import BaseCommand


class Login(BaseCommand):

    def login(self, username, password):
        host = self._gateway.host()
        try:
            self._gateway.form_data('/login', {'username': username, 'password': password})
            logging.getLogger().info("User logged in. %s", {'host': host, 'user': username})
        except CTERAException as error:
            logging.getLogger().error("Login failed. %s", {'host': host, 'user': username})
            raise error

    def logout(self):
        try:
            self._gateway.form_data('/logout', {'foo': 'bar'})
            logging.getLogger().info("User logged out. %s", {'host': self._gateway.host()})
        except CTERAException as error:
            raise error
