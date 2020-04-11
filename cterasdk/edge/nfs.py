import logging

from .enum import Mode
from ..exception import CTERAException
from .base_command import BaseCommand


class NFS(BaseCommand):
    """ Gateway NFS configuration """

    def get_configuration(self):
        """
        Get the current NFS configuration

        :return cterasdk.common.object.Object:
        """
        return self._gateway.get('/config/fileservices/nfs')

    def enable(self):
        """ Enable NFS """
        self._set_mode(True)

    def disable(self):
        """ Disable NFS """
        self._set_mode(False)

    def is_disabled(self):
        """ Check if the NFS server is disabled """
        return self._gateway.get('/config/fileservices/nfs/mode') == Mode.Disabled

    def _set_mode(self, enabled):
        logging.getLogger().info('%s NFS server.', ('Enabling' if enabled else 'Disabling'))
        self._gateway.put('/config/fileservices/nfs/mode', Mode.Enabled if enabled else Mode.Disabled)
        logging.getLogger().info('NFS server %s.', ('enabled' if enabled else 'disabled'))

    def modify(
            self,
            async_write=None,
            aggregate_writes=None):
        """
        Modify the FTP Configuration. Parameters that are not passed will not be affected

        :param bool,optional async_write: If True, use asynchronous writes
        :param bool,optional aggregate_writes: If True, aggregate write requests
        """
        config = self.get_configuration()
        if config.mode != Mode.Enabled:
            raise CTERAException("NFS must be enabled in order to modify its configuration")
        if async_write is not None:
            setattr(config, 'async', Mode.Enabled if async_write else Mode.Disabled)
        if aggregate_writes is not None:
            config.aggregateWrites = Mode.Enabled if aggregate_writes else Mode.Disabled
        self._gateway.put('/config/fileservices/nfs', config)
