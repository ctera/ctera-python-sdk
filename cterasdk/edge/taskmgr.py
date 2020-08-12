import re
import logging

from ..lib.task_manager_base import TaskBase
from ..exception import InputError


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
        logging.getLogger().error('Could not parse task id. %s', {'ref': ref})
        raise InputError('Invalid task id', ref, [64, '/proc/bgtasks/64'])


def running(CTERAHost):
    return CTERAHost.query('/proc/bgtasks', 'status', 'running')


def by_name(CTERAHost, name):
    return CTERAHost.query('/proc/bgtasks', 'name', name)


def wait(CTERAHost, ref):
    task = Task(CTERAHost, ref)
    return task.wait()
