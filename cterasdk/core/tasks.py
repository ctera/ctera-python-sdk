import logging
from ..lib.tasks import AwaitablePortalTask
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


class Tasks(BaseCommand):
    """ Portal Background Task APIs """

    def awaitable_task(self, ref):
        return AwaitablePortalTask(self._core, ref)

    def wait(self, ref, timeout=None, poll_interval=None):
        awaitable_task = AwaitablePortalTask(self._core, ref)
        return awaitable_task.wait(timeout, poll_interval)
