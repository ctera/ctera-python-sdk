import logging
import time
import re

from ..exception import CTERAException, InputError


class TaskStatusEnum:
    Running = "running"
    Warnings = "completed with warnings"
    Failed = "failed"
    Completed = "completed"


class TaskError(CTERAException):

    def __init__(self, task):
        super().__init__()
        self.task = task


class Task:

    def __init__(self, CTERAHost, ref, retries=100, seconds=3):
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
            logging.getLogger().debug('Task info. %s', {
                'id': task.id,
                'name': task.name,
                'status': task.status,
                'message': task.progstring,
                'percentage': task.percentage,
                'start_time': task.startTime,
                'end_time': task.endTime
            })
            self.increment()
            self.running = task.status == TaskStatusEnum.Running
        return self.resolve(task)

    @staticmethod
    def resolve(task):
        if task.status == TaskStatusEnum.Failed:
            logging.getLogger().error('Task failed. %s', {'id': task.id, 'name': task.name})
            raise TaskError(task)
        if task.status == TaskStatusEnum.Warnings:
            logging.getLogger().warning('Task completed with warnings. %s', {'id': task.id, 'name': task.name})
        elif task.status == TaskStatusEnum.Completed:
            logging.getLogger().info('Task completed successfully. %s', {'id': task.id, 'name': task.name})
        else:
            logging.getLogger().warning('Unknown task status. %s', {'id': task.id, 'name': task.name, 'status': task.status})
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
        match = re.search('servers/[^/]*/bgTasks/[1-9][0-9]*$', ref)
        if not match:
            logging.getLogger().error('Invalid task id. %s', {'ref': ref})
            raise InputError('Invalid task id', ref, [64, '/proc/bgtasks/64'])
        return '/' + match.group(0)


def wait(CTERAHost, ref):
    task = Task(CTERAHost, ref)
    return task.wait()
