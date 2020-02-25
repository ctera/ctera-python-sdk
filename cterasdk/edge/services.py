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

    def connect(self, server, user, password, ctera_license=enum.License.EV16):
        Services._validate_license(ctera_license)
        self._check_cttp_traffic(address=server)
        self._check_connection(server)

        param = Object()
        param.server = server
        param.user = user
        param.password = password
        self._connect_to_services(param, ctera_license)

    def activate(self, server, user, code, ctera_license=enum.License.EV16):
        Services._validate_license(ctera_license)
        self._check_cttp_traffic(address=server)

        param = Object()
        param.server = server
        param.user = user
        param.activationCode = code
        self._connect_to_services(param, ctera_license)

    def reconnect(self):
        self._gateway.execute("/status/services", "reconnect", None)

    def disconnect(self):
        self._gateway.put('/config/services', None)

    def enable_sso(self):
        logging.getLogger().info('Enabling single sign-on from CTERA Portal.')
        self._gateway.put('/config/gui/adminRemoteAccessSSO', True)
        logging.getLogger().info('Single sign-on enabled.')

    def _connect_to_services(self, param, ctera_license):
        task = self.attach(param)
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

    def _check_connection(self, server, trust_cert=None):
        param = Object()
        param.server = server
        param.trustCertificate = trust_cert
        obj = self._gateway.execute('/status/services', 'isWebSsoEnabled', param)
        if Services.check_web_sso(obj):
            return
        self._handle_untrusted_cert(server, obj)

    @staticmethod
    def check_web_sso(obj):
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
                    return self.check_connection(server, trust_cert=True)
        except AttributeError:
            pass
        return False

    def attach(self, param):
        logging.getLogger().info("Connecting to Portal. %s", {'server': param.server, 'user': param.user})
        obj = self._gateway.execute("/status/services", "attachAndSave", param)
        return obj.id
