import logging

from .base_command import BaseCommand
from . import session


class Login(BaseCommand):

    def login(self, username, password):
        self._portal.form_data('/login', {'j_username': username, 'j_password': password})

        logging.getLogger().info("User logged in. %s", {'host': self._portal.host(), 'user': username})

        session.activate(self._portal)

    def logout(self):
        self._portal.form_data('/logout', {})

        logging.getLogger().info("User logged out. %s", {'host': self._portal.host()})

        session.terminate(self._portal)
