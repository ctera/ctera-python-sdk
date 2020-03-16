import logging

from ..common import Object
from ..exception import CTERAException
from .base_command import BaseCommand


class Telnet(BaseCommand):
    """ Gateway Telnet configuration APIs """

    def enable(self, code):
        """ Enable Telnet """
        param = Object()
        param.code = code

        logging.getLogger().info("Enabling telnet access.")

        response = self._gateway.execute("/config/device", "startTelnetd", param)
        if response == 'telnetd already running':
            logging.getLogger().info("Telnet access already enabled.")
        elif response != "OK":
            logging.getLogger().error("Failed enabling telnet access. %s", {'reason': response})
            raise CTERAException("Failed enabling telnet access", None, reason=response)
        else:
            logging.getLogger().info("Telnet access enabled.")

    def disable(self):
        """ Disable Telnet """
        logging.getLogger().info("Disabling telnet access.")
        self._gateway.execute("/config/device", "stopTelnetd")
        logging.getLogger().info("Telnet access disabled.")
