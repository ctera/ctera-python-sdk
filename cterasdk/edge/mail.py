import logging

from .types import AlertSettings
from ..common import Object
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Mail(BaseCommand):
    """
    Edge Filer Mail Server configuration APIs

    :ivar cterasdk.edge.mail.alerts alerts: Object holding the Edge Filer e-mail alert APIs
    """

    def __init__(self, edge):
        super().__init__(edge)
        self.alerts = Alerts(self._edge)

    def enable(self, smtp_server, port=25, username=None, password=None, use_tls=True,
               sender=None, recipients=None, min_severity=None):
        """
        Enable e-mail delivery using a custom SMTP server

        :param str smtp_server: Address of the SMTP Server
        :param int,optional port: The listening port of the SMTP Server, defaults to 25
        :param str,optional username: The user name of the SMTP Server, defaults to None
        :param str,optional password: The password of the SMTP Server, defaults to None
        :param bool,optional use_tls: Use TLS when connecting to the SMTP Server, defaults to True
        :param str,optional sender: Sender e-mail address
        :param list[str],optional recipients: List of e-mail recipients
        :param cterasdk.edge.enum.Severity severity: Minimum severity level to trigger email alerts
        """
        settings = self._edge.api.get('/config/logging/alert')
        settings.useCustomServer = True
        settings.SMTPServer = smtp_server

        if settings.port != port:
            settings.port = port

        if username is not None and password is not None:
            settings.useAuth = True
            settings.auth = Object()
            settings.auth._classname = 'AuthSettings'  # pylint: disable=protected-access
            settings.auth.username = username
            settings.auth.password = password

        if settings.useTLS != use_tls:
            settings.useTLS = use_tls

        if sender is not None:
            setattr(settings, 'from', sender)

        if recipients is not None:
            settings.emails = recipients

        if min_severity is not None:
            settings.minSeverity = min_severity

        logger.info('Enabling mail server.')

        self._edge.api.put('/config/logging/alert', settings)

        logger.info(
            'Updated mail server settings. %s',
            {'SMTPServer': smtp_server, 'port': port, 'username': username, 'useTLS': use_tls}
        )

    def disable(self):
        """ Disable e-mail delivery using a custom SMTP server """
        logger.info('Disabling mail server.')
        self._edge.api.put('/config/logging/alert/useCustomServer', False)
        logger.info('Mail server disabled.')


class Alerts(BaseCommand):

    def get(self):
        """
        Get Alert Settings

        :returns: Alert settings
        :rtype: cterasdk.edge.types.AlertSettings
        """
        return AlertSettings.from_server_object(self._edge.api.get('/config/logging/alert/specificAlerts'))

    def modify(self, alerts):
        """
        Modify Alert Settings

        :param cterasdk.edge.types.AlertSettings alerts: Alert Settings
        """
        return AlertSettings.from_server_object(self._edge.api.put('/config/logging/alert/specificAlerts', alerts.to_server_object()))
