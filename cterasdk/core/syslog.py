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

    def enable(self, server, port=514, proto=IPProtocol.UDP, min_severity=Severity.INFO):
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
