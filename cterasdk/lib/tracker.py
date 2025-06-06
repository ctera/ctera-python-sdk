import logging
import time

from ..exceptions import CTERAException


logger = logging.getLogger('cterasdk.common')


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
            logger.debug('Retrieving status. %s', {'ref': self.ref, 'attempt': (self.attempt + 1)})
            self.status = self.CTERAHost.api.get(self.ref)
            logger.debug('Current status. %s', {'ref': self.ref, 'status': self.status})
            self.increment()
            running = self.running()
        return self.resolve()

    def resolve(self):
        if self.successful():
            logger.debug('Success. %s', {'ref': self.ref, 'status': self.status})
            return self.status

        if self.failed():
            logger.debug('Failure. %s', {'ref': self.ref, 'status': self.status})
            raise ErrorStatus(self.status)

        logger.debug('Unknown status. %s', {'ref': self.ref, 'status': self.status})
        raise CTERAException(f'Unknown status: {self.status}')

    def successful(self):
        return self.status in self.success

    def running(self):
        if self.status in self.progress:
            logger.debug('In progress. %s', {'ref': self.ref, 'status': self.status})
            return True

        if self.status in self.transient:
            logger.debug('Transient state. %s', {'ref': self.ref, 'status': self.status})
            return True

        logger.debug('End state. %s', {'ref': self.ref, 'status': self.status})
        return False

    def failed(self):
        return self.status in self.failure

    def increment(self):
        self.attempt = self.attempt + 1
        if self.attempt >= self.retries:
            logger.error('Success criteria for %s was not met. Status: %s', self.ref, self.status)
            raise CTERAException(f'Success criteria for {self.ret} was not met. Status: {self.status}')

        logger.debug('Sleeping for %s seconds.', self.seconds)
        time.sleep(self.seconds)


def track(CTERAHost, ref, success, progress, transient, failure, retries=300, seconds=1):
    tracker = StatusTracker(CTERAHost, ref, success, progress, transient, failure, retries, seconds)
    return tracker.track()
