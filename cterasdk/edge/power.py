import logging
import time

from ..exceptions.transport import HTTPError
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Power(BaseCommand):
    """ Edge Filer Power APIs """

    def reboot(self, wait=False):
        """
        Reboot the Gateway

        :param bool,optional wait: Wait for reboot to complete, defaults to False
        """
        logger.info("Rebooting Edge Filer. %s", {'host': self._edge.host()})
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
        logger.info("Resetting Edge Filer to default settings. %s", {'host': self._edge.host()})
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
                logger.debug("Status check, (try %s)", self._attempt + 1)
                self._edge.test()
                logger.info("Edge Filer is up and running.")
                break
            except ConnectionError:
                logger.debug('Connection error while checking status.')
            except TimeoutError:
                logger.debug('Status check timed out.')
            except HTTPError as e:
                logger.debug("Status check failed with HTTP %s: %s", e.code, e.name)

    def _increment(self):
        self._attempt = self._attempt + 1
        if self._attempt >= self._retries:
            self._unreachable()
        logger.debug("Try %s failed; Sleeping for %s second(s).", self._attempt, self._seconds)
        time.sleep(self._seconds)

    def _unreachable(self):
        host = self._edge.host()
        port = self._edge.port()
        logger.error("Connection timed out after retries. %s", {'host': host, 'port': port})
        raise ConnectionError(f'Connection to {host}:{port} timed out after retries.')
