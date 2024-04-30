import logging

from .base_command import BaseCommand
from ..common import Object
from ..core.enum import Severity, Mode, IPProtocol
from ..exceptions import CTERAException


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
        return self._core.api.get('/settings/logsSettings/syslogConfig/mode') == Mode.Enabled

    def get_configuration(self):
        """
        Retrieve the syslog server configuration
        """
        return self._core.api.get('/settings/logsSettings/syslogConfig')

    def enable(self, server, port=514, protocol=IPProtocol.UDP, min_severity=Severity.INFO):
        """
        Enable Syslog

        :param str server: Syslog server address
        :param int,optional port: Syslog server port
        :param cterasdk.core.enum.IPProtocol,optional protocol: Syslog server IP protocol
        :param cterasdk.core.enum.Severity,optional min_severity: Minimum log severity to forward
        """
        param = Object()
        param._classname = 'PortalSyslogConfig'  # pylint: disable=protected-access
        param.mode = Mode.Enabled
        param.server = server
        param.minSeverity = min_severity
        param.port = port
        param.protocol = protocol
        param.useClientCertificate = False
        logging.getLogger('cterasdk.core').info('Enabling syslog.')
        response = self._core.api.put('/settings/logsSettings/syslogConfig', param)
        logging.getLogger('cterasdk.core').info('Syslog enabled.')
        return response

    def modify(self, server=None, port=None, protocol=None, min_severity=None):
        """
        Modify Syslog log forwarding configuration

        :param str server: Syslog server address
        :param int,optional port: Syslog server port
        :param cterasdk.core.enum.IPProtocol,optional protocol: Syslog server IP protocol
        :param cterasdk.core.enum.Severity,optional min_severity: Minimum log severity to forward
        """
        current_config = self.get_configuration()
        if current_config.mode == Mode.Disabled:
            raise CTERAException("Syslog configuration cannot be modified when disabled")
        if server:
            current_config.server = server
        if port:
            current_config.port = port
        if protocol:
            current_config.protocol = protocol
        if min_severity:
            current_config.minSeverity = min_severity

        logging.getLogger('cterasdk.core').info("Updating syslog server configuration.")
        self._core.api.put('/settings/logsSettings/syslogConfig', current_config)
        logging.getLogger('cterasdk.core').info(
            "Syslog server configured. %s",
            {
                'server': current_config.server,
                'port': current_config.port,
                'protocol': current_config.protocol,
                'minSeverity': current_config.minSeverity
            }
        )

    def disable(self):
        logging.getLogger('cterasdk.core').info('Disabling syslog.')
        response = self._core.api.put('/settings/logsSettings/syslogConfig/mode', Mode.Disabled)
        logging.getLogger('cterasdk.core').info('Syslog disabled.')
        return response
