import logging

from .enum import Mode
from .base_command import BaseCommand


class NTP(BaseCommand):
    """ Gateway NTP configuration """

    def enable(self, servers=None):
        """
        Enable NTP

        :param list[str] servers: List of NTP servers address
        """
        logging.getLogger().info("Enabling time synchronization with ntp servers.")

        self._gateway.put('/config/time/NTPMode', Mode.Enabled)

        logging.getLogger().info("Time synchronization enabled.")

        if servers:
            logging.getLogger().info("Updating time servers. %s", {'servers': servers})

            self._gateway.put('/config/time/NTPServer', servers)

            logging.getLogger().info("Time servers updated. %s", {'servers': servers})

    def disable(self):
        """ Disable NTP """
        logging.getLogger().info("Disabling time synchronization with ntp servers.")

        self._gateway.put('/config/time/NTPMode', Mode.Disabled)

        logging.getLogger().info("Time synchronization disabled.")
