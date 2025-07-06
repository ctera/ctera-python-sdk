import time
import logging
from abc import ABC, abstractmethod
from ..exceptions import CTERAException
from ..convert import tojsonstr


logger = logging.getLogger('cterasdk.common')


class TaskRunningStatus:
    Running = 'running'
    Completed = 'completed'
    Failed = 'failed'
    Warnings = 'completed with warnings'


class TaskError(CTERAException):

    def __init__(self, task):
        super().__init__()
        self.task = task
        if hasattr(task, 'file_details'):
            self.file_details = task.file_details


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

    def wait(self, file_paths=None):
        """
        Wait for task completion

        :param list file_paths: Optional list of file paths for detailed tracking
        """
        task = None
        while self.running:
            logger.debug('Obtaining task status. %s', {'path': self.path, 'attempt': (self.attempt + 1)})
            task = self.get_task_status()
            logger.debug('Task status. %s', tojsonstr(task, False))
            self.increment()
            self.running = task.status == TaskRunningStatus.Running

        if file_paths:
            task.file_details = TaskBase._extract_file_details(task, file_paths)

        resolved_task = TaskBase.resolve(task)

        if file_paths and hasattr(task, 'file_details'):
            resolved_task.file_details = task.file_details

        return resolved_task

    @staticmethod
    def _extract_file_details(task, file_paths):
        """Extract individual file operation details from task info"""
        details = []
        progress_str = getattr(task, 'progstring', '') or getattr(task, 'description', '') or ''

        for file_path in file_paths:
            file_detail = {
                'path': file_path,
                'status': 'completed' if task.status == TaskRunningStatus.Completed else 'failed',
                'error': None
            }

            if task.status in [TaskRunningStatus.Failed, TaskRunningStatus.Warnings]:
                if hasattr(task, 'errorDetails') and task.errorDetails:
                    file_detail['error'] = str(task.errorDetails)
                elif 'failed' in progress_str.lower() or 'error' in progress_str.lower():
                    file_detail['error'] = progress_str
                elif task.status == TaskRunningStatus.Failed:
                    file_detail['error'] = f"Task failed: {getattr(task, 'errorType', 'Unknown error')}"
                else:
                    file_detail['status'] = 'warning'
                    file_detail['error'] = "Completed with warnings"

            details.append(file_detail)

        return details

    @staticmethod
    def resolve(task):
        task_info = {'id': task.id, 'name': task.name, 'status': task.status, 'start_time': task.startTime, 'end_time': task.endTime}
        if task.status == TaskRunningStatus.Failed:
            logger.error('Task failed. %s', task_info)
            raise TaskError(task)
        if task.status == TaskRunningStatus.Warnings:
            logger.warning('Task completed with warnings. %s', task_info)
        if task.status == TaskRunningStatus.Completed:
            logger.debug('Task completed successfully. %s', task_info)
        return task

    def increment(self):
        if self.attempt >= self.retries:
            duration = time.strftime("%H:%M:%S", time.gmtime(self.retries * self.seconds))
            logger.error('Could not obtain task status in a timely manner. %s', {'duration': duration})
            raise CTERAException('Could not obtain task status in a timely manner.')
        self.attempt = self.attempt + 1
        logger.debug('Sleep. %s', {'seconds': self.seconds})
        time.sleep(self.seconds)
