from ..common import Object

import logging

def enable(ctera_host, code):
    
    status = ctera_host.get('/status/device')

    mac = status.MacAddress

    version = status.runningFirmware

    if version.count('.') == 2:

        version = version + '.0'

    param = Object()

    param.code = code

    logging.getLogger().info("Enabling telnet access.")

    ctera_host.execute("/config/device", "startTelnetd", param)

    logging.getLogger().info("Telnet access enabled.")
    
def disable(ctera_host):
    
    logging.getLogger().info("Disabling telnet access.")
        
    ctera_host.execute("/config/device", "stopTelnetd")

    logging.getLogger().info("Telnet access disabled.")