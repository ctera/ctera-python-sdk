import logging

from .enum import Mode
from .base_command import BaseCommand


class NTP(BaseCommand):

    def enable(self, servers=None):
        logging.getLogger().info("Enabling time synchronization with ntp servers.")

        self._gateway.put('/config/time/NTPMode', Mode.Enabled)

        logging.getLogger().info("Time synchronization enabled.")

        if servers:
            logging.getLogger().info("Updating time servers. %s", {'servers': servers})

            self._gateway.put('/config/time/NTPServer', servers)

            logging.getLogger().info("Time servers updated. %s", {'servers': servers})

    def disable(self):
        logging.getLogger().info("Disabling time synchronization with ntp servers.")

        self._gateway.put('/config/time/NTPMode', Mode.Disabled)

        logging.getLogger().info("Time synchronization disabled.")
