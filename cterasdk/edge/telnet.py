import logging

from ..common import Object
from ..exception import CTERAException


def enable(ctera_host, code):
    status = ctera_host.get('/status/device')
    mac = status.MacAddress
    version = status.runningFirmware
    if version.count('.') == 2:
        version = version + '.0'

    param = Object()
    param.code = code

    logging.getLogger().info("Enabling telnet access.")

    response = ctera_host.execute("/config/device", "startTelnetd", param)
    if response == 'telnetd already running':
        logging.getLogger().info("Telnet access already enabled.")
    elif response != "OK":
        logging.getLogger().error("Failed enabling telnet access. %s", {'reason' : response})
        raise CTERAException("Failed enabling telnet access", None, reason=response)
    else:
        logging.getLogger().info("Telnet access enabled.")

def disable(ctera_host):
    logging.getLogger().info("Disabling telnet access.")
    ctera_host.execute("/config/device", "stopTelnetd")
    logging.getLogger().info("Telnet access disabled.")
