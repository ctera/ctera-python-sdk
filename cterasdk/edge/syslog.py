import logging

from ..common import Object
from . import enum
from .base_command import BaseCommand


class Syslog(BaseCommand):
    """ Gateway Syslog configuration APIs """

    def enable(self, server, port=514, proto=enum.IPProtocol.UDP, minSeverity=enum.Severity.INFO):
        """
        Enable Syslog

        :param str server: Server address to send syslog logs
        :param int,optional port: Syslog server communication port, defaults to 514
        :param cterasdk.edge.enum.IPProtocol,optional proto:
         Syslog server communication protocol, defaults to cterasdk.edge.enum.IPProtocol.UDP
        :param cterasdk.edge.enum.Severity,optional minSeverity: Minimal log severity to fetch, defaults to cterasdk.edge.enum.Severity.INFO
        """
        obj = Object()
        obj.mode = enum.Mode.Enabled
        obj.server = server
        obj.port = port
        obj.proto = proto
        obj.minSeverity = minSeverity

        logging.getLogger().info("Configuring syslog server.")
        self._gateway.put('/config/logging/syslog', obj)
        logging.getLogger().info(
            "Syslog server configured. %s",
            {'server': server, 'port': port, 'protocol': proto, 'minSeverity': minSeverity}
        )

    def disable(self):
        """ Disable Syslog """
        logging.getLogger().info("Disabling syslog server.")
        self._gateway.put('/config/logging/syslog/mode', enum.Mode.Disabled)
        logging.getLogger().info("Syslog server disabled.")
