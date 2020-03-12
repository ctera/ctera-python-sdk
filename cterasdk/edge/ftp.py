import logging

from .enum import Mode
from ..exception import CTERAException
from .base_command import BaseCommand


class FTP(BaseCommand):
    """ Gateway FTP configuration APIs """

    def get_configuration(self):
        """
        Get the current FTP configuration

        :return cterasdk.common.object.Object:
        """
        return self._gateway.get('/config/fileservices/ftp')

    def enable(self):
        """ Enable FTP """
        self._set_mode(True)

    def disable(self):
        """ Disable FTP """
        self._set_mode(False)

    def is_disabled(self):
        """ Check if the FTP server is disabled """
        return self._gateway.get('/config/fileservices/ftp/mode') == Mode.Disabled

    def _set_mode(self, enabled):
        logging.getLogger().info('%s FTP server.', ('Enabling' if enabled else 'Disabling'))
        self._gateway.put('/config/fileservices/ftp/mode', Mode.Enabled if enabled else Mode.Disabled)
        logging.getLogger().info('FTP server %s.', ('enabled' if enabled else 'disabled'))

    def modify(
            self,
            allow_anonymous_ftp=None,
            anonymous_download_limit=None,
            anonymous_ftp_folder=None,
            banner_message=None,
            max_connections_per_ip=None,
            require_ssl=None):
        """
        Modify the FTP Configuration. Parameters that are not passed will not be affected

        :param bool,optional allow_anonymous_ftp: Enable/Disable anonymous FTP downloads
        :param int,optional anonymous_download_limit:
         Limit download bandwidth of anonymous connection in KB/sec per connection. 0 for unlimited
        :param str,optional anonymous_ftp_folder: Anonymous FTP Directory
        :param str,optional banner_message: FTP Banner Message
        :param int,optional max_connections_per_ip: Maximum Connections per Client
        :param bool,optional require_ssl: If Ture, allow only SSL/TLS connections
        """
        config = self.get_configuration()
        if config.mode != Mode.Enabled:
            raise CTERAException("FTP must be enabled in order to modify its configuration")
        if anonymous_download_limit is not None:
            config.AnonymousDownloadLimit = anonymous_download_limit
        if anonymous_ftp_folder is not None:
            config.AnonymousFTPFolder = anonymous_ftp_folder
        if allow_anonymous_ftp is not None:
            config.AllowAnonymousFTP = allow_anonymous_ftp
        if banner_message is not None:
            config.BannerMessage = banner_message
        if max_connections_per_ip is not None:
            config.MaxConnectionsPerIP = max_connections_per_ip
        if require_ssl is not None:
            config.RequireSSL = require_ssl
        self._gateway.put('/config/fileservices/ftp', config)
