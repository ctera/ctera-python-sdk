import logging
import time

from ..exceptions import CTERAException
from .base_command import BaseCommand


class Power(BaseCommand):
    """ Edge Filer Power APIs """

    def reboot(self, wait=False):
        """
        Reboot the Gateway

        :param bool,optional wait: Wait for reboot to complete, defaults to False
        """
        logging.getLogger('cterasdk.edge').info("Rebooting device. %s", {'host': self._edge.host()})
        self._edge.api.execute("/status/device", "reboot", None)
        if wait:
            Boot(self._edge).wait()

    def shutdown(self):
        """ Shutdown the Edge Filer"""
        self._edge.api.execute("/status/device", "poweroff", None)

    def reset(self, wait=False):
        """
        Reset the Edge Filer setting

        :param bool,optional wait: Wait for reset to complete, defaults to False
        """
        self._edge.api.execute("/status/device", "reset2default", None)
        logging.getLogger('cterasdk.edge').info("Resetting device to default settings. %s", {'host': self._edge.host()})
        if wait:
            Boot(self._edge).wait()


class Boot:

    def __init__(self, edge, retries=60, seconds=5):
        self._edge = edge
        self._retries = retries
        self._seconds = seconds
        self._attempt = 0

    def wait(self):
        while True:
            try:
                self._increment()
                logging.getLogger('cterasdk.edge').debug('Checking if device is up and running. %s', {'attempt': self._attempt})
                self._edge.test()
                logging.getLogger('cterasdk.edge').info("Device is back up and running.")
                break
            except (CTERAException, ConnectionError, TimeoutError) as e:
                logging.getLogger('cterasdk.edge').debug('Exception. %s', {'exception': e.__class__.__name__, 'message': e.message})

    def _increment(self):
        self._attempt = self._attempt + 1
        if self._attempt >= self._retries:
            self._unreachable()
        logging.getLogger('cterasdk.edge').debug('Sleep. %s', {'seconds': self._seconds})
        time.sleep(self._seconds)

    def _unreachable(self):
        host = self._edge.host()
        port = self._edge.port()
        logging.getLogger('cterasdk.edge').error('Timed out. Could not reach host. %s', {'host': host, 'port': port})
        raise ConnectionError(f'Timed out. Could not reach host {host}:{port}.')
