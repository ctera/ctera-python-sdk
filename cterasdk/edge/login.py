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
            self._gateway.ctera_migrate.login()
        except CTERAException as error:
            logging.getLogger().error("Login failed. %s", {'host': host, 'user': username})
            raise error

    def sso(self, ticket):
        """
        Single Sign On

        :param str ticket: SSO Ticket.
        """
        logging.getLogger().info("Performing Single Sign On.")
        self._gateway.get('/ssologin', {'ticket': ticket})
        self._gateway.ctera_migrate.login()

    def logout(self):
        host = self._gateway.host()
        user = self._gateway.session().user.name
        try:
            self._gateway.form_data('/logout', {'foo': 'bar'})
            logging.getLogger().info("User logged out. %s", {'host': host, 'user': user})
        except CTERAException as error:
            logging.getLogger().error("Logout failed. %s", {'host': host, 'user': user})
            raise error
