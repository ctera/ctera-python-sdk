import logging

from .enum import Mode
from ..exceptions import CTERAException
from .base_command import BaseCommand


class NFS(BaseCommand):
    """ Edge Filer NFS configuration """

    def get_configuration(self):
        """
        Get the current NFS configuration

        :return cterasdk.common.object.Object:
        """
        return self._edge.api.get('/config/fileservices/nfs')

    def enable(self):
        """ Enable NFS """
        self._set_mode(True)

    def disable(self):
        """ Disable NFS """
        self._set_mode(False)

    def is_disabled(self):
        """ Check if the NFS server is disabled """
        return self._edge.api.get('/config/fileservices/nfs/mode') == Mode.Disabled

    def _set_mode(self, enabled):
        logging.getLogger('cterasdk.edge').info('%s NFS server.', ('Enabling' if enabled else 'Disabling'))
        self._edge.api.put('/config/fileservices/nfs/mode', Mode.Enabled if enabled else Mode.Disabled)
        logging.getLogger('cterasdk.edge').info('NFS server %s.', ('enabled' if enabled else 'disabled'))

    def modify(
            self,
            async_write=None,
            aggregate_writes=None,
            mountd_port=None,
            statd_port=None,
            nfsv4_enabled=None,
            krb5_enabled=None,
            nfsd_host=None):
        """
        Modify the FTP Configuration. Parameters that are not passed will not be affected

        :param bool,optional async_write: If True, use asynchronous writes
        :param bool,optional aggregate_writes: If True, aggregate write requests
        :param int,optional mountd_port: Instruct mountd to bind to a specific port
        :param int,optional statd_port: Instruct statd to bind to a specific port
        :param bool,optional nfsv4_enabled: Enable NFSv4
        :param bool,optional krb5_enabled: Enable Kerberos. Note that NFS4V must be enabled to enable Kerberos
        :param str,optional nfsd_host: Instruct nfsd to bind to a specific network interface. Set to an empty string to clear
        """
        config = self.get_configuration()
        if config.mode != Mode.Enabled:
            raise CTERAException("NFS must be enabled in order to modify its configuration")
        if async_write is not None:
            setattr(config, 'async', Mode.Enabled if async_write else Mode.Disabled)
        if aggregate_writes is not None:
            config.aggregateWrites = Mode.Enabled if aggregate_writes else Mode.Disabled
        if mountd_port is not None:
            config.mountdPort = mountd_port
        if statd_port is not None:
            config.statdPort = statd_port
        if nfsv4_enabled is not None:
            config.nfsv4enabled = nfsv4_enabled
        if krb5_enabled is not None:
            if krb5_enabled and config.nfsv4enabled is not None and not config.nfsv4enabled:
                raise CTERAException("NFSv4 must be enabled in order to enable Kerberos")
            config.krb5 = krb5_enabled
        if nfsd_host is not None:
            config.nfsHost = nfsd_host
        self._edge.api.put('/config/fileservices/nfs', config)

    def get_nfs_security(self, name):
        """
        Get the security priority on share NFS authentication mode

        :param str name: The share name
        """
        logging.getLogger('cterasdk.edge').info("Fetching NFS sharing access type and priority. %s", {'share': name})
        return self._edge.api.get('/config/fileservices/share/' + name + '/nfsSec')

    def set_nfs_security(self, name, priority, sectype):
        """
        Set the security priority on share NFS authentication mode

        :param str name: The share name
        :param cterasdk.edge.enum.NFSPriority Priority: Set the Priority for the NFS Security Type
        :param cterasdk.edge.enum.NFSSecurityType Type: Set the Security Method for the NFS Priority
        """
        try:
            logging.getLogger('cterasdk.edge').info(
                "Updating NFS sharing access type and priority. %s",
                {'share': name, 'priority': priority, 'sectype': sectype}
                )
            self._edge.api.put('/config/fileservices/share/' + name + '/nfsSec/' + priority + '/', sectype)
        except Exception as error:
            logging.getLogger('cterasdk.edge').error("Update NFS Security failed.")
            raise CTERAException('Share deletion failed', error)
