import logging

from .enum import Mode
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


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
        logger.info("Enabling time synchronization with ntp servers.")
        self._edge.api.put('/config/time/NTPMode', Mode.Enabled)
        logger.info("Time synchronization enabled.")

        if servers:
            logger.info("Updating time servers. %s", {'servers': servers})
            self._edge.api.put('/config/time/NTPServer', servers)
            logger.info("Time servers updated. %s", {'servers': servers})

    def disable(self):
        """ Disable NTP """
        logger.info("Disabling time synchronization with ntp servers.")
        self._edge.api.put('/config/time/NTPMode', Mode.Disabled)
        logger.info("Time synchronization disabled.")
