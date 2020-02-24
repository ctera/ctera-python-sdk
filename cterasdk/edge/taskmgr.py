import logging
import time
import re

from ..exception import CTERAException, InputError


class TaskStatusEnum:
    Running = "running"
    Failed = "failed"
    Completed = "completed"


class TaskError(CTERAException):

    def __init__(self, task):
        super().__init__()
        self.task = task


class Task:

    def __init__(self, CTERAHost, ref, retries=10, seconds=1):
        self.CTERAHost = CTERAHost
        self.path = self.tid(ref)
        self.attempt = 0
        self.retries = retries
        self.seconds = seconds
        self.running = True

    def wait(self):
        task = None
        while self.running:
            logging.getLogger().debug('Obtaining task status. %s', {'path': self.path, 'attempt': (self.attempt + 1)})
            task = self.CTERAHost.get(self.path)
            self.increment()
            self.running = task.status == TaskStatusEnum.Running
        return self.resolve(task)

    @staticmethod
    def resolve(task):
        if task.status != TaskStatusEnum.Completed:
            logging.getLogger().error('Task did not complete successfully. %s', {'id': task.id, 'status': task.status})
            raise TaskError(task)

        logging.getLogger().debug('Task completed successfully. %s', {'id': task.id})
        return task

    def increment(self):
        if self.attempt >= self.retries:
            duration = time.strftime("%H:%M:%S", time.gmtime(self.retries * self.seconds))
            logging.getLogger().error('Could not obtain task status in a timely manner. %s', {'duration': duration})
            raise CTERAException('Timed out. Could not obtain task status in a timely manner', None, duration=duration)
        self.attempt = self.attempt + 1
        logging.getLogger().debug('Sleep. %s', {'seconds': self.seconds})
        time.sleep(self.seconds)

    @staticmethod
    def tid(ref):
        uid = None
        if isinstance(ref, int):
            uid = str(ref)
        elif isinstance(ref, str):
            match = re.search('[1-9][0-9]*', ref)
            if match is not None:
                start, end = match.span()
                uid = ref[start: end]
        if uid is not None:
            return '/proc/bgtasks/' + uid
        logging.getLogger().error('Could not parse task id. %s', {'ref': ref})
        raise InputError('Invalid task id', ref, [64, '/proc/bgtasks/64'])


def running(CTERAHost):
    return CTERAHost.query('/proc/bgtasks', 'status', 'running')


def by_name(CTERAHost, name):
    return CTERAHost.query('/proc/bgtasks', 'name', name)


def wait(CTERAHost, ref):
    task = Task(CTERAHost, ref)
    return task.wait()
