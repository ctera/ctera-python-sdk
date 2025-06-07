import logging

from ..common import Object
from ..exceptions import CTERAException
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Telnet(BaseCommand):
    """ Edge Filer Telnet configuration APIs """

    def enable(self, code):
        """ Enable Telnet """
        param = Object()
        param.code = code

        logger.info("Enabling telnet access.")

        response = self._edge.api.execute("/config/device", "startTelnetd", param)
        if response == 'telnetd already running':
            logger.info("Telnet already enabled.")
        elif response != "OK":
            logger.error("Failed enabling telnet access. %s", {'reason': response})
            raise CTERAException(f"Failed to enable telnet. Reason: {response}")
        else:
            logger.info("Telnet enabled.")

    def disable(self):
        """ Disable Telnet """
        logger.info("Disabling telnet access.")
        self._edge.api.execute("/config/device", "stopTelnetd")
        logger.info("Telnet disabled.")
