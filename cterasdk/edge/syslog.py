import logging

from ..common import Object
from .enum import Mode


def enable(ctera_host, server, port, proto, minSeverity):
    obj = Object()
    obj.mode = Mode.Enabled
    obj.server = server
    obj.port = port
    obj.proto = proto
    obj.minSeverity = minSeverity

    logging.getLogger().info("Configuring syslog server.")
    ctera_host.put('/config/logging/syslog', obj)
    logging.getLogger().info(
        "Syslog server configured. %s",
        {'server': server, 'port': port, 'protocol': proto, 'minSeverity': minSeverity}
    )


def disable(ctera_host):
    '''
    {
        "desc": "Disable log forwarding over syslog"
    }
    '''

    logging.getLogger().info("Disabling syslog server.")
    ctera_host.put('/config/logging/syslog/mode', Mode.Disabled)
    logging.getLogger().info("Syslog server disabled.")
