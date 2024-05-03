import logging

from ..lib.task_manager_base import TaskError
from ..exceptions import CTERAException
from .base_command import BaseCommand


class Shell(BaseCommand):
    """ Edge Filer Shell command """

    def run_command(self, shell_command, wait=True):
        """
        Execute a Shell Command.

        :param str shell_command: The shell command to execute
        :param bool,optional wait: Wait for the command to execute, defaults to ``True``
        :return: The command result, or the task url path when wait equals ``False``
        """
        logging.getLogger('cterasdk.edge').info("Executing shell command. %s", {'shell_command': shell_command})

        task = self._edge.api.execute("/config/device", "bgshell", shell_command)
        if not wait:
            return task
        try:
            task = self._edge.tasks.wait(task)
            logging.getLogger('cterasdk.edge').info("Shell command executed. %s", {'shell_command': shell_command})
            return task.result.result
        except TaskError as error:
            raise CTERAException('An error occurred while executing task', error)
