import logging

from ..lib.task_manager_base import TaskError
from ..exception import CTERAException
from .base_command import BaseCommand


class Shell(BaseCommand):
    """ Gateway Shell command """

    def run_command(self, shell_command, wait=True):
        """
        Execute a shell command on the gateway

        :param str shell_command: The shell command to execute
        :param bool,optional wait: Wait for the command to execute, defaults to ``True``
        :return: The command result, or the task url path when wait equals ``False``
        """
        logging.getLogger().info("Executing shell command. %s", {'shell_command': shell_command})

        task = self._gateway.execute("/config/device", "bgshell", shell_command)
        if not wait:
            return task
        try:
            task = self._gateway.tasks.wait(task)
            logging.getLogger().info("Shell command executed. %s", {'shell_command': shell_command})
            return task.result.result
        except TaskError as error:
            raise CTERAException('An error occurred while executing task', error)
