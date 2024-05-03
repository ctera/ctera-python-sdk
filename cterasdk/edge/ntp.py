import logging

from .enum import Mode
from .base_command import BaseCommand


class NTP(BaseCommand):
    """ Edge Filer NTP configuration """

    def get_configuration(self):
        return self._edge.api.get('/config/time')

    @property
    def servers(self):
        return self._edge.api.get('/config/time/NTPServer')

    def enable(self, servers=None):
        """
        Enable NTP

        :param list[str] servers: List of NTP servers address
        """
        logging.getLogger('cterasdk.edge').info("Enabling time synchronization with ntp servers.")
        self._edge.api.put('/config/time/NTPMode', Mode.Enabled)
        logging.getLogger('cterasdk.edge').info("Time synchronization enabled.")

        if servers:
            logging.getLogger('cterasdk.edge').info("Updating time servers. %s", {'servers': servers})
            self._edge.api.put('/config/time/NTPServer', servers)
            logging.getLogger('cterasdk.edge').info("Time servers updated. %s", {'servers': servers})

    def disable(self):
        """ Disable NTP """
        logging.getLogger('cterasdk.edge').info("Disabling time synchronization with ntp servers.")
        self._edge.api.put('/config/time/NTPMode', Mode.Disabled)
        logging.getLogger('cterasdk.edge').info("Time synchronization disabled.")
