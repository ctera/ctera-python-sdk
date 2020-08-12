import re
import logging

from ..lib.task_manager_base import TaskBase
from ..exception import InputError


class Task(TaskBase):

    def _get_task_id(self, ref):
        match = re.search('servers/[^/]*/bgTasks/[1-9][0-9]*$', ref)
        if not match:
            logging.getLogger().error('Invalid task id. %s', {'ref': ref})
            raise InputError('Invalid task id', ref, ['servers/server/bgTasks/107781'])
        return '/' + match.group(0)


def wait(CTERAHost, ref):
    task = Task(CTERAHost, ref, retries=100, seconds=3)
    return task.wait()
