import logging

from .enum import Mode
from ..exceptions import CTERAException
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class RSync(BaseCommand):
    """ Edge Filer RSync configuration """

    def get_configuration(self):
        """
        Get the current RSync configuration

        :return cterasdk.common.object.Object:
        """
        return self._edge.api.get('/config/fileservices/rsync')

    def enable(self):
        """ Enable FTP """
        self._set_mode(True)

    def disable(self):
        """ Disable FTP """
        self._set_mode(False)

    def is_disabled(self):
        """ Check if the Rsync server is disabled """
        return self._edge.api.get('/config/fileservices/rsync/server') == Mode.Disabled

    def _set_mode(self, enabled):
        """ Disable RSync """
        logger.info('%s RSync server.', ('Enabling' if enabled else 'Disabling'))
        self._edge.api.put('/config/fileservices/rsync/server', Mode.Enabled if enabled else Mode.Disabled)
        logger.info('RSync server %s.', ('enabled' if enabled else 'disabled'))

    def modify(
            self,
            port=None,
            max_connections=None):
        """
        Modify the RSync Configuration. Parameters that are not passed will not be affected

        :param int,optional port: RSync Port
        :param int,optional max_connections: Maximum Connections
        """
        config = self.get_configuration()
        if config.server != Mode.Enabled:
            raise CTERAException("RSync must be enabled in order to modify its configuration")
        if port is not None:
            config.port = port
        if max_connections is not None:
            config.maxConnections = max_connections
        self._edge.api.put('/config/fileservices/rsync', config)
