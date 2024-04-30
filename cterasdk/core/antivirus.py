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
        self.servers = AntivirusServers(self._core)

    def list_servers(self, include=None):
        """
        List the antivirus servers

        :param list[str],optional include: List of fields to retrieve, defaults to ``['name', 'type']``
        """
        include = union(include or [], Antivirus.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._core, '/antiviruses', param)

    def rescan(self):
        """
        Scan all files using the latest antivirus update. This may take a while
        """
        logging.getLogger('cterasdk.core').info("Starting antivirus rescan.")
        self._core.api.execute('/servers', 'resetAllAVBG')
        logging.getLogger('cterasdk.core').info("Started antivirus rescan.")

    def suspend(self):
        """
        Suspend antivirus scanning
        """
        logging.getLogger('cterasdk.core').info("Suspending antivirus scanning.")
        self._core.api.put('/settings/cloudFSSettings/antivirusSettings/isEnabled', False)
        logging.getLogger('cterasdk.core').info("Suspended antivirus scanning.")

    def unsuspend(self):
        """
        Unsuspend antivirus scanning
        """
        logging.getLogger('cterasdk.core').info("Unsuspending antivirus scanning.")
        self._core.api.put('/settings/cloudFSSettings/antivirusSettings/isEnabled', True)
        logging.getLogger('cterasdk.core').info("Unsuspended antivirus scanning.")

    def status(self):
        """
        Get antivirus service status
        """
        param = Object()
        param.icapService = ICAPServices.Antivirus
        return self._core.api.execute('', 'getIcapGlobalStatus', param)


class AntivirusServers(BaseCommand):

    def get(self, name):
        """
        Get an antivirus server's configuration

        :param str name: Server name
        """
        return self._core.api.get(f'/antiviruses/{name}')

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
        logging.getLogger('cterasdk.core').info("Adding antivirus server. %s", {'name': name, 'type': vendor, 'url': url})
        response = self._core.api.add('/antiviruses', param)
        logging.getLogger('cterasdk.core').info("Added antivirus server. %s", {'name': name, 'type': vendor, 'url': url})
        return response

    def delete(self, name):
        """
        Remove an antivirus server
        """
        return self._core.api.delete(f'/antiviruses/{name}')

    def suspend(self, name):
        """
        Suspend an antivirus server
        """
        logging.getLogger('cterasdk.core').info("Suspending antivirus server. %s", {'name': name})
        self._core.api.put(f'/antiviruses/{name}/enabled', False)
        logging.getLogger('cterasdk.core').info("Suspended antivirus server. %s", {'name': name})

    def unsuspend(self, name):
        """
        Unsuspend antivirus scanning
        """
        logging.getLogger('cterasdk.core').info("Unsuspending antivirus server. %s", {'name': name})
        self._core.api.put(f'/antiviruses/{name}/enabled', True)
        logging.getLogger('cterasdk.core').info("Unsuspended antivirus server. %s", {'name': name})
