import logging

from ..common import Object
from .base_command import BaseCommand


class Mail(BaseCommand):
    """ Edge Filer Mail Server configuration APIs """

    def enable(self, smtp_server, port=25, username=None, password=None, use_tls=True):
        """
        Enable e-mail delivery using a custom SMTP server

        :param str smtp_server: Address of the SMTP Server
        :param int,optional port: The listening port of the SMTP Server, defaults to 25
        :param str,optional username: The user name of the SMTP Server, defaults to None
        :param str,optional password: The password of the SMTP Server, defaults to None
        :param bool,optional use_tls: Use TLS when connecting to the SMTP Server, defaults to True
        """
        settings = self._edge.api.get('/config/logging/alert')
        settings.useCustomServer = True
        settings.SMTPServer = smtp_server

        if settings.port != port:
            settings.port = port

        if username is not None and password is not None:
            settings.useAuth = True
            settings.auth = Object()
            settings.auth.username = username
            settings.auth.password = password

        if settings.useTLS != use_tls:
            settings.useTLS = use_tls

        logging.getLogger('cterasdk.edge').info('Enabling mail server.')

        self._edge.api.put('/config/logging/alert', settings)

        logging.getLogger('cterasdk.edge').info(
            'Updated mail server settings. %s',
            {'SMTPServer': smtp_server, 'port': port, 'username': username, 'useTLS': use_tls}
        )

    def disable(self):
        """ Disable e-mail delivery using a custom SMTP server """
        logging.getLogger('cterasdk.edge').info('Disabling mail server.')
        self._edge.api.put('/config/logging/alert/useCustomServer', False)
        logging.getLogger('cterasdk.edge').info('Mail server disabled.')
