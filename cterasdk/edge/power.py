import logging
import time

from ..exception import HostUnreachable, ExhaustedException
from .base_command import BaseCommand


class Power(BaseCommand):
    """ Gateway Power APIs """

    def reboot(self, wait=False):
        """
        Reboot the Gateway

        :param bool,optional wait: Wait got the reboot to complete, defaults to False
        """
        logging.getLogger().info("Rebooting device. %s", {'host': self._gateway.host()})
        self._gateway.execute("/status/device", "reboot", None)
        if wait:
            Boot(self._gateway).wait()

    def shutdown(self):
        """ Shutdown the Gateway """
        self._gateway.execute("/status/device", "poweroff", None)

    def reset(self, wait=False):
        """
        Reset the Gateway setting

        :param bool,optional wait: Wait got the reset to complete, defaults to False
        """
        self._gateway.execute("/status/device", "reset2default", None)
        logging.getLogger().info("Resetting device to default settings. %s", {'host': self._gateway.host()})
        if wait:
            Boot(self._gateway).wait()


class Boot:

    def __init__(self, gateway, retries=60, seconds=5):
        self._gateway = gateway
        self._retries = retries
        self._seconds = seconds
        self._attempt = 0

    def wait(self):
        while True:
            try:
                self._increment()
                logging.getLogger().debug('Checking if device is up and running. %s', {'attempt': self._attempt})
                self._gateway.test()
                logging.getLogger().info("Device is back up and running.")
                break
            except (HostUnreachable, ExhaustedException) as e:
                logging.getLogger().debug('Exception. %s', {'exception': e.classname, 'message': e.message})

    def _increment(self):
        self._attempt = self._attempt + 1
        if self._attempt >= self._retries:
            self._unreachable()
        logging.getLogger().debug('Sleep. %s', {'seconds': self._seconds})
        time.sleep(self._seconds)

    def _unreachable(self):
        scheme = self._gateway.scheme()
        host = self._gateway.host()
        port = self._gateway.port()

        logging.getLogger().error('Timed out. Could not reach host. %s', {'scheme': scheme, 'host': host, 'port': port})
        raise HostUnreachable(None, host, port, scheme)
