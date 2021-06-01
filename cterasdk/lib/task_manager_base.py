import time
import logging
from abc import ABC, abstractmethod
from ..exception import CTERAException
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
        if retries <= 0:
            raise ValueError("retries must be bigger than 0")
        if seconds <= 0:
            raise ValueError("seconds must be bigger than 0")

        self.CTERAHost = CTERAHost
        self.path = self._get_task_id(ref)
        self.retries = retries
        self.seconds = seconds

    @abstractmethod
    def _get_task_id(self, ref):
        raise NotImplementedError("Subclass must implement _get_task_id")

    @abstractmethod
    def get_task_status(self):
        raise NotImplementedError("Subclass must implement get_task_status")

    def wait(self):
        task = None
        for i in range(self.retries):
            logging.getLogger().debug('Obtaining task status. %s', {'path': self.path, 'attempt': (i + 1)})
            task = self.get_task_status()
            logging.getLogger().debug('Task status. %s', tojsonstr(task, False))
            if task.status != TaskRunningStatus.Running:
                break
            logging.getLogger().debug('Sleep. %s', {'seconds': self.seconds})
            time.sleep(self.seconds)
        return self.resolve(task)

    def resolve(self, task):
        if task.status == TaskRunningStatus.Running:
            duration = time.strftime("%H:%M:%S", time.gmtime(self.retries * self.seconds))
            logging.getLogger().error('Could not obtain task status in a timely manner. %s', {'duration': duration})
            raise CTERAException('Timed out. Could not obtain task status in a timely manner', None, duration=duration)

        task_info = {'id': task.id, 'name': task.name, 'status': task.status, 'start_time': task.startTime, 'end_time': task.endTime}
        if task.status == TaskRunningStatus.Failed:
            logging.getLogger().error('Task failed. %s', task_info)
            raise TaskError(task)
        if task.status == TaskRunningStatus.Warnings:
            logging.getLogger().warning('Task completed with warnings. %s', task_info)
        if task.status == TaskRunningStatus.Completed:
            logging.getLogger().debug('Task completed successfully. %s', task_info)
        return task
