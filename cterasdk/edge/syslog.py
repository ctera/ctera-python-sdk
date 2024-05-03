import logging

from ..exceptions import CTERAException
from ..common import Object
from . import enum
from .base_command import BaseCommand


class Syslog(BaseCommand):
    """ Edge Filer Syslog configuration APIs """

    def enable(self, server, port=514, proto=enum.IPProtocol.UDP, min_severity=enum.Severity.INFO):
        """
        Enable Syslog

        :param str server: Server address to send syslog logs
        :param int,optional port: Syslog server communication port, defaults to 514
        :param cterasdk.edge.enum.IPProtocol,optional proto:
         Syslog server communication protocol, defaults to cterasdk.edge.enum.IPProtocol.UDP
        :param cterasdk.edge.enum.Severity,optional min_severity:
         Minimal log severity to fetch, defaults to cterasdk.edge.enum.Severity.INFO
        """
        obj = Object()
        obj.mode = enum.Mode.Enabled
        obj.server = server
        obj.port = port
        obj.proto = proto
        obj.minSeverity = min_severity

        logging.getLogger('cterasdk.edge').info("Configuring syslog server.")
        self._edge.api.put('/config/logging/syslog', obj)
        logging.getLogger('cterasdk.edge').info(
            "Syslog server configured. %s",
            {'server': server, 'port': port, 'protocol': proto, 'minSeverity': min_severity}
        )

    def disable(self):
        """ Disable Syslog """
        logging.getLogger('cterasdk.edge').info("Disabling syslog server.")
        self._edge.api.put('/config/logging/syslog/mode', enum.Mode.Disabled)
        logging.getLogger('cterasdk.edge').info("Syslog server disabled.")

    def get_configuration(self):
        return self._edge.api.get('/config/logging/syslog')

    def modify(self, server=None, port=None, proto=None, min_severity=None):
        """
        Modify current Syslog configuration. Only configurations that are not None will be changed. Syslog must be enabled

        :param str,optional server: Server address to send syslog logs
        :param int,optional port: Syslog server communication port
        :param cterasdk.edge.enum.IPProtocol,optional proto: Syslog server communication protocol
        :param cterasdk.edge.enum.Severity,optional min_severity: Minimal log severity to fetch
        """
        current_config = self.get_configuration()
        if current_config.mode == enum.Mode.Disabled:
            raise CTERAException("Syslog configuration cannot be modified when disabled")
        if server:
            current_config.server = server
        if port:
            current_config.port = port
        if proto:
            current_config.proto = proto
        if min_severity:
            current_config.minSeverity = min_severity

        logging.getLogger('cterasdk.edge').info("Updating syslog server configuration.")
        self._edge.api.put('/config/logging/syslog', current_config)
        logging.getLogger('cterasdk.edge').info(
            "Syslog server configured. %s",
            {
                'server': current_config.server,
                'port': current_config.port,
                'protocol': current_config.proto,
                'minSeverity': current_config.minSeverity
            }
        )
