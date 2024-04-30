import time
import logging
from abc import ABC, abstractmethod
from ..exceptions import CTERAException
from ..convert import tojsonstr


class TaskRunningStatus:
    Running = 'running'
    Completed = 'completed'
    Failed = 'failed'
    Warnings = 'completed with warnings'


class TaskError(CTERAException):

    def __init__(self, task):
        super().__init__()
        self.task = task


class TaskBase(ABC):

    def __init__(self, CTERAHost, ref, retries=10, seconds=1):
        self.CTERAHost = CTERAHost
        self.path = self._get_task_id(ref)
        self.attempt = 0
        self.retries = retries
        self.seconds = seconds
        self.running = True

    @abstractmethod
    def _get_task_id(self, ref):
        raise NotImplementedError("Subclass must implement _get_task_id")

    @abstractmethod
    def get_task_status(self):
        raise NotImplementedError("Subclass must implement get_task_status")

    def wait(self):
        task = None
        while self.running:
            logging.getLogger('cterasdk.common').debug('Obtaining task status. %s', {'path': self.path, 'attempt': (self.attempt + 1)})
            task = self.get_task_status()
            logging.getLogger('cterasdk.common').debug('Task status. %s', tojsonstr(task, False))
            self.increment()
            self.running = task.status == TaskRunningStatus.Running
        return TaskBase.resolve(task)

    @staticmethod
    def resolve(task):
        task_info = {'id': task.id, 'name': task.name, 'status': task.status, 'start_time': task.startTime, 'end_time': task.endTime}
        if task.status == TaskRunningStatus.Failed:
            logging.getLogger('cterasdk.common').error('Task failed. %s', task_info)
            raise TaskError(task)
        if task.status == TaskRunningStatus.Warnings:
            logging.getLogger('cterasdk.common').warning('Task completed with warnings. %s', task_info)
        if task.status == TaskRunningStatus.Completed:
            logging.getLogger('cterasdk.common').debug('Task completed successfully. %s', task_info)
        return task

    def increment(self):
        if self.attempt >= self.retries:
            duration = time.strftime("%H:%M:%S", time.gmtime(self.retries * self.seconds))
            logging.getLogger('cterasdk.common').error('Could not obtain task status in a timely manner. %s', {'duration': duration})
            raise CTERAException('Timed out. Could not obtain task status in a timely manner', None, duration=duration)
        self.attempt = self.attempt + 1
        logging.getLogger('cterasdk.common').debug('Sleep. %s', {'seconds': self.seconds})
        time.sleep(self.seconds)
