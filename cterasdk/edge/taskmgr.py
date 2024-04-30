import re
import logging

from . import query
from ..common import Object
from ..lib.task_manager_base import TaskBase
from ..exceptions import InputError
from .base_command import BaseCommand


class Task(TaskBase):

    def _get_task_id(self, ref):
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
        logging.getLogger('cterasdk.edge').error('Could not parse task id. %s', {'ref': ref})
        raise InputError('Invalid task id', ref, [64, '64', '/proc/bgtasks/64'])

    def get_task_status(self):
        return self.CTERAHost.api.get(self.path)


class Tasks(BaseCommand):
    """ Edge Filer Background Task APIs """

    def status(self, ref):
        """
        Get background task status

        :param str ref: Task reference
        """
        task = Task(self._edge, ref)
        return task.status()

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

    def wait(self, ref, retries=100, seconds=1):
        """
        Wait for background task to complete

        :param str ref: Task reference
        :param int,optional retries: Number of retries when sampling the task status, defaults to 100
        :param int,optional seconds: Number of seconds to wait between retries, defaults to 1
        """
        task = Task(self._edge, ref, retries, seconds)
        return task.wait()
