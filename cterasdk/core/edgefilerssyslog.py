import logging

from ..common import Object
from .enum import IPProtocol
from .base_command import BaseCommand


class EdgeFilersSyslog(BaseCommand):
    """
    Portal Edge Filers syslog APIs

    :ivar cterasdk.core.edgefilerssyslog.EdgeFilersSyslog servers: Object holding the Portal Edge Filers syslog server APIs
    """

    def list_servers(self):
        """
        List the Edge Filers syslog servers
        """
        return self._portal.get('/microservices/syslog/status/servers')

    def delete(self, address):
        """
        Delete the Edge Filers syslog server
        """
        logging.getLogger().info("Deleting Edge Filers syslog server.")
        self._portal.delete(f'/microservices/syslog/settings/servers/{address}')
        logging.getLogger().info("Deleted Edge Filers syslog server.")

    def delete_servers(self, servers):
        """
        Delete the Edge Filers syslog server
        """
        for server in servers:
            self.delete(server)

    def add(self, address, port=514, protocol=IPProtocol.UDP, message_threshold=100):
        """
        Add an Edge Filers syslog server

        :param str address: Edge Filers syslog server name
        :param int port: Syslog server port, defaults to 514
        :param cterasdk.core.enum.IPProtocol,optional protocol: Syslog server IP protocol
        :param int message_threshold: Defines the message threshold queue, defaults to '100'
        """
        param = Object()
        param._classname = "SyslogServerConfig"  # pylint: disable=protected-access
        param.address = address
        param.port = port
        param.protocol = protocol
        param.messagesLagThreshold = message_threshold
        logging.getLogger().info("Adding Edge Filers syslog server.")
        self._portal.post('/microservices/syslog/settings/servers', param)
        logging.getLogger().info("Added Edge Filers syslog server.")

    def enable(self):
        """
        Enable the Syslog Server
        """

        logging.getLogger().info("Enabling the Edge Filers syslog server.")
        self._portal.put('/microservices/syslog/settings/enabled', True)
        logging.getLogger().info("Enabled Edge Filers syslog server.")

    def disable(self):
        """
        Disabling the Syslog Server
        """

        logging.getLogger().info("Disabling the Edge Filers syslog server.")
        self._portal.put('/microservices/syslog/settings/enabled', False)
        logging.getLogger().info("Disabling Edge Filers syslog server.")
