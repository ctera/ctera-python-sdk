import logging
import time

from ..exception import CTERAException


class ErrorStatus(CTERAException):

    def __init__(self, status):
        super().__init__()
        self.status = status


class StatusTracker:

    def __init__(self, CTERAHost, ref, success, progress, transient, failure, retries, seconds):
        self.CTERAHost = CTERAHost
        self.ref = ref
        self.success = success
        self.progress = progress
        self.transient = transient
        self.failure = failure
        self.retries = retries
        self.seconds = seconds
        self.attempt = 0
        self.status = None

    def track(self):
        running = True
        while running:
            logging.getLogger().debug('Retrieving status. %s', {'ref': self.ref, 'attempt': (self.attempt + 1)})
            self.status = self.CTERAHost.get(self.ref)
            logging.getLogger().debug('Current status. %s', {'ref': self.ref, 'status': self.status})
            self.increment()
            running = self.running()
        return self.resolve()

    def resolve(self):
        if self.successful():
            logging.getLogger().debug('Success. %s', {'ref': self.ref, 'status': self.status})
            return self.status

        if self.failed():
            logging.getLogger().debug('Failure. %s', {'ref': self.ref, 'status': self.status})
            raise ErrorStatus(self.status)

        logging.getLogger().debug('Unknown status. %s', {'ref': self.ref, 'status': self.status})
        raise CTERAException('Unknown status', None, status=self.status)

    def successful(self):
        return self.status in self.success

    def running(self):
        if self.status in self.progress:
            logging.getLogger().debug('In progress. %s', {'ref': self.ref, 'status': self.status})
            return True

        if self.status in self.transient:
            logging.getLogger().debug('Transient state. %s', {'ref': self.ref, 'status': self.status})
            return True

        logging.getLogger().debug('End state. %s', {'ref': self.ref, 'status': self.status})
        return False

    def failed(self):
        return self.status in self.failure

    def increment(self):
        self.attempt = self.attempt + 1
        if self.attempt >= self.retries:
            logging.getLogger().error('Status did not meet success criteria. %s', {'ref': self.ref, 'status': self.status})
            raise CTERAException('Timed out. Status did not meet success criteria', None, ref=self.ref, status=self.status)

        logging.getLogger().debug('Sleep. %s', {'seconds': self.seconds})
        time.sleep(self.seconds)


def track(CTERAHost, ref, success, progress, transient, failure, retries=300, seconds=1):
    tracker = StatusTracker(CTERAHost, ref, success, progress, transient, failure, retries, seconds)
    return tracker.track()
