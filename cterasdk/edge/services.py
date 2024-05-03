import logging
import cterasdk.settings

from ..lib.task_manager_base import TaskError
from .licenses import Licenses
from ..lib import ask, track
from ..common import Object
from ..exceptions import CTERAException, InputError
from . import enum
from .base_command import BaseCommand
from .types import TCPService


class Services(BaseCommand):
    """ Edge Filer Cloud Services configuration APIs """
    _UNTRUSTED_CERTIFICATE_ERRORS = [
        'UntrustedCert',
        'UntrustedCA',
        'UntrustedCertExpired',
        'UntrustedCertSelfSigned',
        'UntrustedCertDNS'
    ]

    def __init__(self, edge):
        super().__init__(edge)
        self._trust_cert = {}

    def get_status(self):
        """
        Retrieve the cloud services connection status
        """
        status = self._edge.api.get('/status/services')
        connection = Object()
        connection.connected = status.CTERAPortal.connectionState == enum.ServicesConnectionState.Connected
        if connection.connected:
            connection.ipaddr = status.CTERAPortal.connectedAddress
            connection.user = status.userDisplayName
            connection.server_version = status.portalVersion
            connection.server_address = status.CTERAPortal.serverList[0].name
            connection.last_connected_at = status.CTERAPortal.establishedTime
        return connection

    def connected(self):
        """
        Check if the Edge Filer is connected to CTERA Portal
        """
        return self._edge.api.get('/status/services/CTERAPortal/connectionState') == enum.ServicesConnectionState.Connected

    def _before_connect_to_services(self, ctera_license, server):
        Services._validate_license(ctera_license)
        if self._edge.network.proxy.is_enabled():
            logging.getLogger('cterasdk.edge').debug('Skipping TCP connection verification over port 995.')
        else:
            self._check_cttp_traffic(address=server)

    def connect(self, server, user, password, ctera_license=enum.License.EV16):
        """
        Connect to a Portal.\n
        The connect method will first validate the `license` argument,
         ensure the Edge Filer can establish a TCP connection over port 995 to the Portal and
         verify the Portal does not require device activation via code.
         TCP connection verification over port 995 is skipped when the Edge Filer is configured to use a proxy.

        :param str server: Address of the Portal
        :param str user: User for the Portal connection
        :param str password: Password for the Portal connection
        :param cterasdk.edge.enum.License,optional ctera_license: CTERA License, defaults to cterasdk.edge.enum.License.EV16
        """
        self._before_connect_to_services(ctera_license, server)
        self._check_connection(server)

        param = Object()
        param.server = server
        param.user = user
        param.password = password
        param.trustCertificate = self._trust_cert.get(server, False)
        self._connect_to_services(param, ctera_license)

    def activate(self, server, user, code, ctera_license=enum.License.EV16):
        """
        Enroll the Edge Filer with CTERA Portal using an activation code

        :param str server: Address of the Portal
        :param str user: User for  the Portal connection
        :param str code: Activation code for the Portal connection
        :param cterasdk.edge.enum.License,optional ctera_license: CTERA License, defaults to cterasdk.edge.enum.License.EV16
        """
        self._before_connect_to_services(ctera_license, server)

        param = Object()
        param.server = server
        param.user = user
        param.activationCode = code
        param.trustCertificate = self._trust_cert.get(server, False)
        self._connect_to_services(param, ctera_license)

    def reconnect(self):
        """ Reconnect to the Portal """
        self._edge.api.execute("/status/services", "reconnect", None)

    def disconnect(self):
        """ Disconnect from the Portal """
        self._edge.api.put('/config/services', None)

    def sso_enabled(self):
        """
        Is SSO connection enabled

        :return bool: True if SSO connection is enabled, else False
        """
        return self._edge.api.get('/config/gui/adminRemoteAccessSSO')

    def enable_sso(self):
        """ Enable SSO connection """
        self._set_sso(True)

    def disable_sso(self):
        """ Disable SSO connection """
        self._set_sso(False)

    def _set_sso(self, sso_state):
        logging.getLogger('cterasdk.edge').info('%s single sign-on from CTERA Portal.', ('Enabling' if sso_state else 'Disabling'))
        self._edge.api.put('/config/gui/adminRemoteAccessSSO', sso_state)
        logging.getLogger('cterasdk.edge').info('Single sign-on %s.', ('enabled' if sso_state else 'disabled'))

    def _connect_to_services(self, param, ctera_license):
        task = self._attach(param)
        try:
            self._edge.tasks.wait(task)
            track(self._edge, '/status/services/CTERAPortal/connectionState', [enum.ServicesConnectionState.Connected],
                  [enum.ServicesConnectionState.ResolvingServers, enum.ServicesConnectionState.Connecting,
                   enum.ServicesConnectionState.Attaching, enum.ServicesConnectionState.Authenticating],
                  [], [enum.ServicesConnectionState.Disconnected], 20, 1)
            logging.getLogger('cterasdk.edge').info("Connected to Portal.")
        except TaskError as error:
            description = error.task.description
            logging.getLogger('cterasdk.edge').error("Connection failed. Reason: %s", description)
            raise CTERAException("Connection failed", None, reason=description)
        self._edge.licenses.apply(ctera_license)

    @staticmethod
    def _validate_license(ctera_license):
        try:
            Licenses.infer(ctera_license)
        except InputError as error:
            logging.getLogger('cterasdk.edge').error('Connection failed. Invalid license type. %s', {'license': ctera_license})
            raise error

    def _check_cttp_traffic(self, address, port=995):
        tcp_connect_result = self._edge.network.tcp_connect(TCPService(address, port))
        if not tcp_connect_result.is_open:
            logging.getLogger('cterasdk.edge').error("Unable to establish connection over port %s", str(tcp_connect_result.port))
            raise ConnectionError(f'Unable to establish CTTP connection {tcp_connect_result.host}:{tcp_connect_result.port}')

    def _check_connection(self, server):
        param = Object()
        param.server = server
        param.trustCertificate = self._trust_cert.get(server, False)
        obj = self._edge.api.execute('/status/services', 'isWebSsoEnabled', param)
        if not Services._check_web_sso(obj):
            self._handle_untrusted_cert(server, obj)

    @staticmethod
    def _check_web_sso(obj):
        try:
            if obj.result.hasWebSSO:
                message = "Connection failed. You must activate this Edge Filer using an activation code."
                logging.getLogger('cterasdk.edge').error(message)
                raise CTERAException(message)

            if not obj.result.hasWebSSO and obj.rc == "connectOK":
                return True
            raise CTERAException("Connection failed", None, reason=obj.rc)
        except AttributeError:
            pass

        return False

    def _handle_untrusted_cert(self, server, obj):
        try:
            if obj.rc in Services._UNTRUSTED_CERTIFICATE_ERRORS:
                proceed = False
                if cterasdk.settings.sessions.management.edge.services.ssl == 'prompt':
                    logging.getLogger('cterasdk.edge').warning(msg=obj.msg)
                    proceed = ask(f"Connect {self._edge.host()} to {server}?")
                if cterasdk.settings.sessions.management.edge.services.ssl is False or proceed:
                    self._trust_cert[server] = True
                    return self._check_connection(server)
        except AttributeError:
            pass
        return False

    def _attach(self, param):
        logging.getLogger('cterasdk.edge').info("Connecting to Portal. %s", {'server': param.server, 'user': param.user})
        obj = self._edge.api.execute("/status/services", "attachAndSave", param)
        return obj.id
