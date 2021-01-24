import logging

from ..common import Object, union
from . import query
from .enum import ICAPServices
from .base_command import BaseCommand


class Antivirus(BaseCommand):
    """
    Portal Antivirus APIs

    :ivar cterasdk.core.antivirus.AntivirusServers servers: Object holding the Portal antivirus server APIs
    """

    default = ['name', 'type']

    def __init__(self, portal):
        super().__init__(portal)
        self.servers = AntivirusServers(self._portal)

    def list_servers(self, include=None):
        """
        List the antivirus servers

        :param list[str],optional include: List of fields to retrieve, defaults to ``['name', 'type']``
        """
        include = union(include or [], Antivirus.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._portal, '/antiviruses', param)

    def rescan(self):
        """
        Scan all files using the latest antivirus update. This may take a while
        """
        logging.getLogger().info("Starting antivirus rescan.")
        self._portal.execute('/servers', 'resetAllAVBG')
        logging.getLogger().info("Started antivirus rescan.")

    def suspend(self):
        """
        Suspend antivirus scanning
        """
        logging.getLogger().info("Suspending antivirus scanning.")
        self._portal.put('/settings/cloudFSSettings/antivirusSettings/isEnabled', False)
        logging.getLogger().info("Suspended antivirus scanning.")

    def unsuspend(self):
        """
        Unsuspend antivirus scanning
        """
        logging.getLogger().info("Unsuspending antivirus scanning.")
        self._portal.put('/settings/cloudFSSettings/antivirusSettings/isEnabled', True)
        logging.getLogger().info("Unsuspended antivirus scanning.")

    def status(self):
        """
        Get antivirus service status
        """
        param = Object()
        param.icapService = ICAPServices.Antivirus
        return self._portal.execute('', 'getIcapGlobalStatus', param)


class AntivirusServers(BaseCommand):

    def get(self, name):
        """
        Get an antivirus server's configuration

        :param str name: Server name
        """
        return self._portal.get('/antiviruses/%s' % name)

    def add(self, name, vendor, url, connection_timeout=5):
        """
        Add an antivirus server

        :param str name: Server name
        :param cterasdk.core.enum.AntivirusType vendor: Server type
        :param str url: Server URL (example: ``http://your-antivirus.server.local:1234/signature``)
        :param int,optional connection_timeout: Server connection timeout (in seconds), defaults to 5 seconds
        """
        param = Object()
        param._classname = 'Antivirus'  # pylint: disable=protected-access
        param.name = name
        param.type = vendor
        param.serverUrl = url
        param.connectionTimeoutSeconds = connection_timeout
        logging.getLogger().info("Adding antivirus server. %s", {'name': name, 'type': vendor, 'url': url})
        response = self._portal.add('/antiviruses', param)
        logging.getLogger().info("Added antivirus server. %s", {'name': name, 'type': vendor, 'url': url})
        return response

    def delete(self, name):
        """
        Remove an antivirus server
        """
        return self._portal.delete('/antiviruses/%s' % name)

    def suspend(self, name):
        """
        Suspend an antivirus server
        """
        logging.getLogger().info("Suspending antivirus server. %s", {'name': name})
        self._portal.put('/antiviruses/%s/enabled' % name, False)
        logging.getLogger().info("Suspended antivirus server. %s", {'name': name})

    def unsuspend(self, name):
        """
        Unsuspend antivirus scanning
        """
        logging.getLogger().info("Unsuspending antivirus server. %s", {'name': name})
        self._portal.put('/antiviruses/%s/enabled' % name, True)
        logging.getLogger().info("Unsuspended antivirus server. %s", {'name': name})
