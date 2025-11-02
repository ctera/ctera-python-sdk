import re
import time
import logging
import asyncio
from datetime import datetime
from abc import ABC, abstractmethod

from ..common import Object
from ..common.enum import TaskRunningStatus
from ..exceptions.common import TaskWaitTimeoutError, AwaitableTaskException
from ..exceptions.transport import HTTPError


logger = logging.getLogger('cterasdk.common')


class BaseTask(Object):
    """
    Base Task

    :ivar int id: Task ID
    :ivar str name: Task name
    :ivar datetime.datetime start_time: Start time
    :ivar int elapsed_time: Elapsed time
    :ivar cterasdk.common.enum.TaskRunningStatus status: Status
    :ivar int percentage: Percentage
    :ivar datetime.datetime end_time: End time
    :ivar cterasdk.common.object.Object result: Task result
    """
    def __init__(self, task):
        super().__init__()
        self.id = task.id
        self.name = task.name
        self.start_time = datetime.fromisoformat(task.startTime)
        self.elapsed_time = task.elapsedTime
        self.status = task.status
        self.percentage = task.percentage
        self.end_time = datetime.fromisoformat(task.endTime) if task.endTime is not None else None
        self.result = task.result

    @property
    def failed(self):
        return self.status == TaskRunningStatus.Failed

    @property
    def completed_with_warnings(self):
        return self.status == TaskRunningStatus.Warnings

    @property
    def completed(self):
        return self.status == TaskRunningStatus.Completed


class EdgeTask(BaseTask):
    """
    Edge Task

    :ivar str description: Task description
    """
    def __init__(self, task):
        super().__init__(task)
        self.description = task.description


class PortalTask(BaseTask):
    """
    Portal Task

    :ivar str progress_str: Task progress description
    :ivar int tenant: Tenant UID
    """
    def __init__(self, task):
        super().__init__(task)
        self.progress_str = task.progstring
        self.tenant = task.portalUid


class FilesystemTask(PortalTask):
    """
    Filesystem Task

    :ivar int files_processed: Files processed
    :ivar int bytes_processed: Bytes processed
    :ivar int total_files: Total files
    :ivar int total_bytes: Total bytes
    :ivar str error_type: Task error
    :ivar str file_in_progress: File in progress
    :ivar int user_uid: User UID
    :ivar cterasdk.common.object.Object cursor: Cursor
    """
    def __init__(self, task):
        super().__init__(task)
        self.files_processed = task.filesProcessed
        self.bytes_processed = task.bytesProcessed
        self.total_files = task.totalFiles
        self.total_bytes = task.totalBytes
        self.error_type = task.errorType
        self.file_in_progress = task.fileInProgress
        self.user_uid = task.userUid
        self.cursor = task.cursor


class AwaitableTask(ABC):

    def __init__(self, ctera, ref):
        self._ctera = ctera
        self._ref = self._task_reference(ref)

    @property
    def ref(self):
        return self._ref

    def wait(self, timeout=None, poll_interval=None):
        """
        Wait until the given task is complete, or until the timeout expires.

        If a positive `timeout` (in seconds) is specified, this function will block
        only up to that duration. If `timeout` is None or non-positive, it will
        wait indefinitely until the task completes.

        :param float,optional timeout: Raise exception in the event of a timeout
        :param float,optional poll_interval: Poll interval, defaults to 1 second
        """
        try:
            return _synchronous_wait(self, timeout, poll_interval)
        except HTTPError as error:
            raise AwaitableTaskException(f"An error occurred while retrieving the status of Task '{self.ref}'.",
                                         self._ctera.tasks.awaitable_task(self.ref)) from error

    async def a_wait(self, timeout=None, poll_interval=None):
        """
        Wait until the given task is complete, or until the timeout expires.

        If a positive `timeout` (in seconds) is specified, this function will block
        only up to that duration. If `timeout` is None or non-positive, it will
        wait indefinitely until the task completes.

        :param float,optional timeout: Raise exception in the event of a timeout
        :param float,optional poll_interval: Poll interval, defaults to 1 second
        """
        try:
            return await _asynchronous_wait(self, timeout, poll_interval)
        except HTTPError as error:
            raise AwaitableTaskException(f"An error occurred while retrieving the status of Task '{self.ref}'.",
                                         self._ctera.tasks.awaitable_task(self.ref)) from error

    @abstractmethod
    def _task_reference(self, ref):
        raise NotImplementedError("Subclass must implement the '_task_reference' function.")

    @abstractmethod
    def _task_status_object(self, task):
        raise NotImplementedError("Subclass must implement the '_task_status_object' function.")

    @abstractmethod
    def status(self):
        raise NotImplementedError("Subclass must implement the 'status' function.")

    @abstractmethod
    async def a_status(self):
        raise NotImplementedError("Subclass must implement the 'a_status' function.")

    def __str__(self):
        return self._ref

    def __repr__(self):
        return str(self)


class AwaitableEdgeTask(AwaitableTask):
    """
    Awaitable Edge Filer Task Object
    """
    def _task_reference(self, ref):
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
        logger.error('Failed to parse task identifier from reference: %s', ref)
        raise ValueError(f'Failed to parse task identifier from reference: {ref}')

    def _task_status_object(self, task):
        return EdgeTask(task)

    def status(self):
        """
        Synchronous function to retrieve task status.
        """
        return self._task_status_object(self._ctera.api.get(self._ref))

    async def a_status(self):
        """
        Asynchronous function to retrieve task status.
        """
        return self._task_status_object(await self._ctera.api.get(self._ref))


class AwaitablePortalTask(AwaitableTask):
    """
    Awaitable Portal Task Object
    """
    def _task_reference(self, ref):
        match = re.search('servers/[^/]*/bgTasks/[1-9][0-9]*$', ref)
        if not match:
            logger.error('Failed to parse task identifier from reference: %s', ref)
            raise ValueError(f'Failed to parse task identifier from reference: {ref}')
        return match.group(0)

    def _task_status_object(self, task):
        if task._classname == 'FileManagerBgTask':  # pylint: disable=protected-access
            return FilesystemTask(task)
        return PortalTask(task)

    def status(self):
        """
        Synchronous function to retrieve task status.
        """
        if self._ctera.session().in_tenant_context():
            return self._task_status_object(self._ctera.api.execute('', 'getTaskStatus', self._ref))
        return self._task_status_object(self._ctera.api.get(f'{self._ref}'))

    async def a_status(self):
        """
        Asynchronous function to retrieve task status.
        """
        if self._ctera.session().in_tenant_context():
            return self._task_status_object(await self._ctera.v1.api.execute('', 'getTaskStatus', self._ref))
        return self._task_status_object(await self._ctera.v1.api.get(f'{self._ref}'))


def _before_wait(timeout, poll_interval):
    timeout_at = None

    if timeout is not None:
        if not isinstance(timeout, (int, float)):
            raise ValueError('Timeout must be a positive int or float.')
        timeout_at = time.time() + timeout

    if poll_interval is not None and isinstance(poll_interval, (int, float)):
        raise ValueError('Poll interval must be a positive int or float.')
    poll_interval = poll_interval if poll_interval is not None else 1

    return timeout_at, poll_interval


def _synchronous_wait(awaitable_task, timeout=None, poll_interval=None):
    timeout_at, poll_interval = _before_wait(timeout, poll_interval)
    while True:
        task = awaitable_task.status()
        if task.status in [
            TaskRunningStatus.Completed,
            TaskRunningStatus.Disabled,
            TaskRunningStatus.Stopped,
            TaskRunningStatus.Warnings,
            TaskRunningStatus.Failed,
        ]:
            return task
        if timeout_at is not None and time.time() > timeout_at:
            raise TaskWaitTimeoutError(timeout, task)
        time.sleep(poll_interval)


async def _asynchronous_wait(awaitable_task, timeout=None, poll_interval=None):
    timeout_at, poll_interval = _before_wait(timeout, poll_interval)
    while True:
        task = await awaitable_task.a_status()
        if task.status in [
            TaskRunningStatus.Completed,
            TaskRunningStatus.Disabled,
            TaskRunningStatus.Stopped,
            TaskRunningStatus.Warnings,
            TaskRunningStatus.Failed,
        ]:
            return task
        if timeout_at is not None and time.time() > timeout_at:
            raise TaskWaitTimeoutError(timeout, task)
        await asyncio.sleep(poll_interval)
