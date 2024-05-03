import re
import logging

from ..lib.task_manager_base import TaskBase
from ..exceptions import InputError
from .base_command import BaseCommand


class Task(TaskBase):

    def _get_task_id(self, ref):
        match = re.search('servers/[^/]*/bgTasks/[1-9][0-9]*$', ref)
        if not match:
            logging.getLogger('cterasdk.core').error('Invalid task id. %s', {'ref': ref})
            raise InputError('Invalid task id', ref, ['servers/server/bgTasks/107781'])
        return match.group(0)

    def get_task_status(self):
        if self.CTERAHost.session().in_tenant_context():
            return self.CTERAHost.api.execute('', 'getTaskStatus', self.path)
        return self.CTERAHost.api.get('/' + self.path)


class Tasks(BaseCommand):
    """ Portal Background Task APIs """

    def status(self, ref):
        """
        Get background task status

        :param str ref: Task reference
        """
        task = Task(self._core, ref)
        return task.status()

    def wait(self, ref, retries=100, seconds=1):
        """
        Wait for background task to complete

        :param str ref: Task reference
        :param int,optional retries: Number of retries when sampling the task status, defaults to 100
        :param int,optional seconds: Number of seconds to wait between retries, defaults to 1
        """
        task = Task(self._core, ref, retries, seconds)
        return task.wait()
