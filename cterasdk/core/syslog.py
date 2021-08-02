import logging

from .base_command import BaseCommand
from ..common import Object
from ..core.enum import Severity, Mode, IPProtocol


class Syslog(BaseCommand):
    """
    Portal Syslog Management APIs
    """

    # TODO: upload_ca_certificate  # pylint: disable=W0511
    # TODO: upload_client_certificate  # pylint: disable=W0511

    def is_enabled(self):
        """
        Check if forwarding log messages over syslog is enabled
        """
        return self._portal.get('/settings/logsSettings/syslogConfig/mode') == Mode.Enabled

    def get_configuration(self):
        """
        Retrieve the syslog server configuration
        """
        return self._portal.get('/settings/logsSettings/syslogConfig')

    def enable(self, server, port=514, proto=IPProtocol.UDP, min_severity=Severity.INFO):
        """
        Enable Syslog

        :param str server: Syslog server address
        :param int,optional port: Syslog server port
        :param cterasdk.core.enum.IPProtocol,optional proto: Syslog server IP protocol
        :param cterasdk.core.enum.Severity,optional min_severity: Minimum log severity to forward
        """
        param = Object()
        param._classname = 'PortalSyslogConfig'  # pylint: disable=protected-access
        param.mode = Mode.Enabled
        param.server = server
        param.minSeverity = min_severity
        param.port = port
        param.protocol = proto
        param.useClientCertificate = False
        logging.getLogger().info('Enabling syslog.')
        response = self._portal.put('/settings/logsSettings/syslogConfig', param)
        logging.getLogger().info('Syslog enabled.')
        return response

    def disable(self):
        logging.getLogger().info('Disabling syslog.')
        response = self._portal.put('/settings/logsSettings/syslogConfig/mode', Mode.Disabled)
        logging.getLogger().info('Syslog disabled.')
        return response
