import logging
from .base_command import BaseCommand


class Mail(BaseCommand):
    """ Portal Mail Server Configuration APIs """

    def is_enabled(self):
        """
        Check if forwarding log messages over syslog is enabled
        """
        return self._core.api.get('/settings/enableEmailSending') is True

    def enable(self, host=None, port=None, sender=None, username=None, password=None, use_tls=None):
        """
        Enable Mail Server Notifications

        :param str,optional host: SMTP host
        :param str,optional port: SMTP port
        :param str,optional sender: Sender e-mail address
        :param str,optional username: The user name of the SMTP Server, defaults to None
        :param str,optional password: The password of the SMTP Server, defaults to None
        :param bool,optional use_tls: Use TLS when connecting to the SMTP Server, defaults to None
        """
        settings = self._core.api.get('/settings')
        settings.enableEmailSending = True
        settings = Mail._configure_settings(settings, host, port, sender, username, password, use_tls)
        logging.getLogger('cterasdk.core').info('Enabling Mail Server.')
        response = self._core.api.put('/settings', settings)
        logging.getLogger('cterasdk.core').info('Mail Server enabled.')
        return response

    def disable(self):
        """
        Disable Mail Server Notifications
        """
        logging.getLogger('cterasdk.core').info('Disabling Mail Server.')
        response = self._core.api.put('/settings/enableEmailSending', False)
        logging.getLogger('cterasdk.core').info('Mail Server disabled.')
        return response

    @staticmethod
    def _configure_settings(settings, host, port, sender, username, password, use_tls):
        if host is not None:
            settings.smtpSettings.smtpHost = host
        if port is not None:
            settings.smtpSettings.smtpPort = port
        if username is not None and password is not None:
            settings.smtpSettings.user = username
            settings.smtpSettings.password = password
        if use_tls is not None:
            settings.smtpSettings.enableTls = use_tls
        if sender is not None:
            settings.defaultPortalSettings.mailSettings.sender = sender
        return settings

    def modify(self, host=None, port=None, sender=None, username=None, password=None, use_tls=None):
        """
        Modify Mail Server Configuration

        :param str,optional host: SMTP host
        :param str,optional port: SMTP port
        :param str,optional sender: Sender e-mail address
        :param str,optional username: The user name of the SMTP Server, defaults to None
        :param str,optional password: The password of the SMTP Server, defaults to None
        :param bool,optional use_tls: Use TLS when connecting to the SMTP Server, defaults to None
        """
        settings = self._core.api.get('/settings')
        settings = Mail._configure_settings(settings, host, port, sender, username, password, use_tls)
        logging.getLogger('cterasdk.core').info('Modifying Mail Server settings.')
        response = self._core.api.put('/settings', settings)
        logging.getLogger('cterasdk.core').info('Mail Server settings modified.')
        return response
