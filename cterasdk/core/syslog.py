import logging
from pathlib import Path


from .base_command import BaseCommand
from ..common import Object
from ..core.enum import Severity, Mode, IPProtocol
from ..exceptions import CTERAException
from ..lib import X509Certificate, PrivateKey
from ..clients.common import MultipartForm


class Syslog(BaseCommand):
    """
    Portal Syslog Management APIs
    """

    def import_ca(self, certificate):
        """
        Import the Syslog Server CA certificate

        :param str certificate: Path to the PEM-encoded CA certificate.
        """
        X509Certificate.load_certificate(certificate)
        logging.getLogger('cterasdk.edge').info("Uploading syslog server CA certificate.")
        self._import_secret('/settings/logSettings/syslogConfig/caCertificateUpload', certificate)
        logging.getLogger('cterasdk.edge').info("Uploaded syslog server CA certificate.")

    def import_client_certificate(self, private_key, certificate):
        """
        Import the Syslog Server CA certificate

        :param str private_key: Path to the PEM-encoded private key.
        :param str certificate: Path to the PEM-encoded client certificate.
        """
        PrivateKey.load_private_key(private_key)
        logging.getLogger('cterasdk.edge').info("Uploading syslog server private key.")
        self._import_secret('/settings/logSettings/syslogConfig/clientPrivateKeyUpload', private_key)
        logging.getLogger('cterasdk.edge').info("Uploaded syslog server private key.")

        X509Certificate.load_certificate(certificate)
        logging.getLogger('cterasdk.edge').info("Uploading syslog server client certificate.")
        self._import_secret('/settings/logSettings/syslogConfig/clientCertificateUpload', certificate)
        logging.getLogger('cterasdk.edge').info("Uploaded syslog server client certificate.")

    def _import_secret(self, path, file):
        """
        Import a Syslog Certificate or Private Key

        :param str path: URL Path
        :param str file: File Path
        """
        handle = Path(file)
        with handle.open('rb') as fd:
            form = MultipartForm()
            form.add('name', handle.name)
            form.add('firmware_path', fd, handle.name)
            self._core.api.multipart(path, form)

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

    def enable(self, server, port=514, protocol=IPProtocol.UDP, min_severity=Severity.INFO, ca_cert=None):
        """
        Enable Syslog

        :param str server: Syslog server address
        :param int,optional port: Syslog server port
        :param cterasdk.core.enum.IPProtocol,optional protocol: Syslog server IP protocol
        :param cterasdk.core.enum.Severity,optional min_severity: Minimum Log Severity
        :param str,optional ca_cert: Path to the PEM-encoded CA certificate.
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
        if protocol == IPProtocol.TCP and ca_cert is not None:
            self.import_ca(ca_cert)
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
