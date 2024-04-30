import logging

from ..exceptions import CTERAException
from .base_command import BaseCommand


class Login(BaseCommand):

    def info(self):
        """
        Get login info
        """
        return self._edge.api.get('/nosession/logininfo')

    def login(self, username, password):
        host = self._edge.host()
        try:
            self._edge.api.form_data('/login', {'username': username, 'password': password})
            logging.getLogger('cterasdk.edge').info("User logged in. %s", {'host': host, 'user': username})
            self._edge.ctera_migrate.login()
        except CTERAException:
            logging.getLogger('cterasdk.edge').error("Login failed. %s", {'host': host, 'user': username})
            raise

    def sso(self, ticket):
        """
        Single Sign On

        :param str ticket: SSO Ticket.
        """
        logging.getLogger('cterasdk.edge').info("Performing Single Sign On.")
        self._edge.api.get('/ssologin', params={'ticket': ticket})
        self._edge.ctera_migrate.login()

    def logout(self):
        host = self._edge.host()
        user = self._edge.session().user.name
        try:
            self._edge.api.form_data('/logout', {'foo': 'bar'})
            logging.getLogger('cterasdk.edge').info("User logged out. %s", {'host': host, 'user': user})
        except CTERAException:
            logging.getLogger('cterasdk.edge').error("Logout failed. %s", {'host': host, 'user': user})
            raise
