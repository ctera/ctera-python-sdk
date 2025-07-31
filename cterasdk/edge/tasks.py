import logging

from . import query
from ..lib.tasks import AwaitableEdgeTask
from ..common import Object
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Tasks(BaseCommand):
    """ Edge Filer Background Task APIs """

    def awaitable_task(self, ref):
        return AwaitableEdgeTask(self._edge, ref)

    def wait(self, ref, timeout=None, poll_interval=None):
        awaitable_task = AwaitableEdgeTask(self._edge, ref)
        return awaitable_task.wait(timeout, poll_interval)

    def running(self):
        """
        Get all running background tasks
        """
        return self._query('status', 'running')

    def by_name(self, name):
        """
        Get background tasks by name

        :param str name: Task name
        """
        return self._query('name', name)

    def _query(self, key, value):
        param = Object()
        param.key = key
        param.value = value
        return query.iterator(self._edge, '/proc/bgtasks', param)
