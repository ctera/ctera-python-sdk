import logging

from .licenses import Licenses
from . import taskmgr as TaskManager
from ..lib import ask
from ..common import Object
from ..exception import CTERAException, InputError, CTERAConnectionError
from .. import config
from . import enum
from .base_command import BaseCommand


class Services(BaseCommand):
    """ Gateway Cloud Services configuration APIs """

    def __init__(self, gateway):
        super().__init__(gateway)
        self._trust_cert = {}

    def get_status(self):
        """
        Retrieve the cloud services connection status
        """
        status = self._gateway.get('/status/services')
        connection = Object()
        connection.connected = (status.CTERAPortal.connectionState == enum.ServicesConnectionState.Connected)
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
        return self._gateway.get('/status/services/CTERAPortal/connectionState') == enum.ServicesConnectionState.Connected

    def connect(self, server, user, password, ctera_license=enum.License.EV16):
        """
        Connect to a Portal.\n
        The connect method will first validate the `license` argument,
         ensure the Gateway can establish a TCP connection over port 995 to `server` using :py:func:`Gateway.tcp_connect()` and
         verify the Portal does not require device activation via code

        :param str server: Address of the Portal
        :param str user: User for the Portal connection
        :param str password: Password for the Portal connection
        :param cterasdk.edge.enum.License,optional ctera_license: CTERA License, defaults to cterasdk.edge.enum.License.EV16
        """
        Services._validate_license(ctera_license)
        self._check_cttp_traffic(address=server)
        self._check_connection(server)

        param = Object()
        param.server = server
        param.user = user
        param.password = password
        param.trustCertificate = self._trust_cert.get(server, False)
        self._connect_to_services(param, ctera_license)

    def activate(self, server, user, code, ctera_license=enum.License.EV16):
        """
        Activate the gateway using an activation code

        :param str server: Address of the Portal
        :param str user: User for  the Portal connection
        :param str code: Activation code for the Portal connection
        :param cterasdk.edge.enum.License,optional ctera_license: CTERA License, defaults to cterasdk.edge.enum.License.EV16
        """
        Services._validate_license(ctera_license)
        self._check_cttp_traffic(address=server)

        param = Object()
        param.server = server
        param.user = user
        param.activationCode = code
        param.trustCertificate = self._trust_cert.get(server, False)
        self._connect_to_services(param, ctera_license)

    def reconnect(self):
        """ Reconnect to the Portal """
        self._gateway.execute("/status/services", "reconnect", None)

    def disconnect(self):
        """ Disconnect from the Portal """
        self._gateway.put('/config/services', None)

    def sso_enabled(self):
        """
        Is SSO connection enabled

        :return bool: True if SSO connection is enabled, else False
        """
        return self._gateway.get('/config/gui/adminRemoteAccessSSO')

    def enable_sso(self):
        """ Enable SSO connection """
        self._set_sso(True)

    def disable_sso(self):
        """ Disable SSO connection """
        self._set_sso(False)

    def _set_sso(self, sso_state):
        logging.getLogger().info('%s single sign-on from CTERA Portal.', ('Enabling' if sso_state else 'Disabling'))
        self._gateway.put('/config/gui/adminRemoteAccessSSO', sso_state)
        logging.getLogger().info('Single sign-on %s.', ('enabled' if sso_state else 'disabled'))

    def _connect_to_services(self, param, ctera_license):
        task = self._attach(param)
        try:
            TaskManager.wait(self._gateway, task)
            logging.getLogger().info("Connected to Portal.")
        except TaskManager.TaskError as error:
            description = error.task.description
            logging.getLogger().error("Connection failed. Reason: %s", description)
            raise CTERAException("Connection failed", None, reason=description)
        self._gateway.licenses.apply(ctera_license)

    @staticmethod
    def _validate_license(ctera_license):
        try:
            Licenses.infer(ctera_license)
        except InputError as error:
            logging.getLogger().error('Connection failed. Invalid license type. %s', {'license': ctera_license})
            raise error

    def _check_cttp_traffic(self, address, port=995):
        tcp_conn_status = self._gateway.network.tcp_connect(address=address, port=port)
        if not tcp_conn_status:
            logging.getLogger().error("Unable to establish connection over port %s", str(port))
            raise CTERAConnectionError('Unable to establish connection', None, host=address, port=port, protocol='CTTP')

    def _check_connection(self, server):
        param = Object()
        param.server = server
        param.trustCertificate = self._trust_cert.get(server, False)
        obj = self._gateway.execute('/status/services', 'isWebSsoEnabled', param)
        if not Services._check_web_sso(obj):
            self._handle_untrusted_cert(server, obj)

    @staticmethod
    def _check_web_sso(obj):
        try:
            if obj.result.hasWebSSO:
                message = "Connection failed. You must activate this Gateway using an activation code."
                logging.getLogger().error(message)
                raise CTERAException(message)

            if not obj.result.hasWebSSO and obj.rc == "connectOK":
                return True
            raise CTERAException("Connection failed", None, reason=obj.rc)
        except AttributeError:
            pass

        return False

    def _handle_untrusted_cert(self, server, obj):
        try:
            if obj.rc in ['UntrustedCert', 'UntrustedCA']:
                if config.connect['ssl'] == 'Consent':
                    logging.getLogger().warning(msg=obj.msg)
                    proceed = ask("Proceed connecting '" + self._gateway.host() + "' to " + server + '?')
                if config.connect['ssl'] == 'Trust' or proceed:
                    self._trust_cert[server] = True
                    return self._check_connection(server)
        except AttributeError:
            pass
        return False

    def _attach(self, param):
        logging.getLogger().info("Connecting to Portal. %s", {'server': param.server, 'user': param.user})
        obj = self._gateway.execute("/status/services", "attachAndSave", param)
        return obj.id
