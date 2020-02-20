import logging

from .enum import Mode


def enable(ctera_host, servers):
    logging.getLogger().info("Enabling time synchronization with ntp servers.")

    ctera_host.put('/config/time/NTPMode', Mode.Enabled)

    logging.getLogger().info("Time synchronization enabled.")

    if len(servers) > 0:
        logging.getLogger().info("Updating time servers. %s", {'servers' : servers})

        ctera_host.put('/config/time/NTPServer', servers)

        logging.getLogger().info("Time servers updated. %s", {'servers' : servers})


def disable(ctera_host):
    logging.getLogger().info("Disabling time synchronization with ntp servers.")

    ctera_host.put('/config/time/NTPMode', Mode.Disabled)

    logging.getLogger().info("Time synchronization disabled.")
