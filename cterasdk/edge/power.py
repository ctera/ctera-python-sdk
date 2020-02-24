import logging
import time

from ..exception import HostUnreachable, ExhaustedException


def reboot(CTERAHost, wait):
    logging.getLogger().info("Rebooting device. %s", {'host': CTERAHost.host()})
    CTERAHost.execute("/status/device", "reboot", None)
    if wait:
        Boot(CTERAHost).wait()


def shutdown(ctera_host):
    ctera_host.execute("/status/device", "poweroff", None)


def reset(CTERAHost, wait):
    CTERAHost.execute("/status/device", "reset2default", None)
    logging.getLogger().info("Resetting device to default settings. %s", {'host': CTERAHost.host()})
    if wait:
        Boot(CTERAHost).wait()


class Boot:

    def __init__(self, CTERAHost, retries=60, seconds=5):
        self.CTERAHost = CTERAHost
        self.retries = retries
        self.seconds = seconds
        self.attempt = 0

    def wait(self):
        while True:
            try:
                self.increment()
                logging.getLogger().debug('Checking if device is up and running. %s', {'attempt': self.attempt})
                self.CTERAHost.test()
                logging.getLogger().info("Device is back up and running.")
                break
            except (HostUnreachable, ExhaustedException) as e:
                logging.getLogger().debug('Exception. %s', {'exception': e.classname, 'message': e.message})

    def increment(self):
        self.attempt = self.attempt + 1
        if self.attempt >= self.retries:
            self.unreachable()
        logging.getLogger().debug('Sleep. %s', {'seconds': self.seconds})
        time.sleep(self.seconds)

    def unreachable(self):
        scheme = self.CTERAHost.scheme()
        host = self.CTERAHost.host()
        port = self.CTERAHost.port()

        logging.getLogger().error('Timed out. Could not reach host. %s', {'scheme': scheme, 'host': host, 'port': port})
        raise HostUnreachable(None, host, port, scheme)
