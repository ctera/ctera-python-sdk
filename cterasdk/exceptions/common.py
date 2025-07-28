from .base import CTERAException


class AwaitableTaskException(CTERAException):

    def __init__(self, message, awaitable_task):
        """
        Awaitable Task Exception

        :param cterasdk.lib.tasks.AwaitableTask awaitable_task: Awaitable task object
        """
        super().__init__(message)
        self.awaitable_task = awaitable_task


class TaskException(CTERAException):
    """
    Task Exception

    :param cterasdk.common.object.Object task: Task object
    """
    def __init__(self, message, task):
        super().__init__(message)
        self.task = task


class TaskWaitTimeoutError(TaskException):
    """
    Task Wait Timeout Error
    """
    def __init__(self, duration, task):
        super().__init__(f"Task {task.id} remains pending completion after {duration} second(s).", task)
