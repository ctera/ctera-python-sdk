import logging

from .licenses import infer
from .network import tcp_connect
from . import taskmgr as TaskManager
from ..lib import ask
from ..common import Object
from ..exception import CTERAException, InputError, CTERAConnectionError
from .. import config


def connect(ctera_host, server, user, password, ctera_license):
    validate_license(ctera_license)
    check_cttp_traffic(ctera_host, address=server)
    check_connection(ctera_host, server)

    param = Object()
    param.server = server
    param.user = user
    param.password = password
    connect_to_services(ctera_host, param, ctera_license)


def activate(ctera_host, server, user, code, ctera_license):
    validate_license(ctera_license)
    check_cttp_traffic(ctera_host, address=server)

    param = Object()
    param.server = server
    param.user = user
    param.activationCode = code
    connect_to_services(ctera_host, param, ctera_license)


def connect_to_services(ctera_host, param, ctera_license):
    task = attach(ctera_host, param)
    try:
        TaskManager.wait(ctera_host, task)
        logging.getLogger().info("Connected to Portal.")
    except TaskManager.TaskError as error:
        description = error.task.description
        logging.getLogger().error("Connection failed. Reason: %s", description)
        raise CTERAException("Connection failed", None, reason=description)
    ctera_host.apply_license(ctera_license)


def validate_license(ctera_license):
    try:
        infer(ctera_license)
    except InputError as error:
        logging.getLogger().error('Connection failed. Invalid license type. %s', {'license' : ctera_license})
        raise error


def check_cttp_traffic(ctera_host, address, port=995):
    tcp_conn_status = tcp_connect(ctera_host, address=address, port=port)
    if not tcp_conn_status:
        logging.getLogger().error("Unable to establish connection over port %s", str(port))
        raise CTERAConnectionError('Unable to establish connection', None, host=address, port=port, protocol='CTTP')


def check_connection(ctera_host, server, trust_cert=None):
    param = Object()
    param.server = server
    param.trustCertificate = trust_cert
    obj = ctera_host.execute('/status/services', 'isWebSsoEnabled', param)
    if check_web_sso(obj):
        return
    handle_untrusted_cert(ctera_host, server, obj)


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


def handle_untrusted_cert(ctera_host, server, obj):
    try:
        if obj.rc in ['UntrustedCert', 'UntrustedCA']:
            if config.connect['ssl'] == 'Consent':
                logging.getLogger().warning(msg=obj.msg)
                proceed = ask("Proceed connecting '" + ctera_host.host() + "' to " + server + '?')
            if config.connect['ssl'] == 'Trust' or proceed:
                return check_connection(ctera_host, server, trust_cert=True)
    except AttributeError:
        pass
    return False


def attach(ctera_host, param):
    logging.getLogger().info("Connecting to Portal. %s", {'server' : param.server, 'user' : param.user})
    obj = ctera_host.execute("/status/services", "attachAndSave", param)
    return obj.id


def reconnect(ctera_host):
    ctera_host.execute("/status/services", "reconnect", None)


def disconnect(ctera_host):
    ctera_host.put('/config/services', None)


def enable_sso(ctera_host):
    logging.getLogger().info('Enabling single sign-on from CTERA Portal.')
    ctera_host.put('/config/gui/adminRemoteAccessSSO', True)
    logging.getLogger().info('Single sign-on enabled.')
