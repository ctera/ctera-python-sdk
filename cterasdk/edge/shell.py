import logging

from ..exceptions import CTERAException
from ..exceptions.common import TaskException
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Shell(BaseCommand):
    """ Edge Filer Shell command """

    def run_command(self, shell_command, wait=True):
        """
        Execute a Shell Command.

        :param str shell_command: The shell command to execute
        :param bool,optional wait: Wait for the command to execute, defaults to ``True``
        :return: The command result, or the task url path when wait equals ``False``
        """
        logger.info("Executing shell command. %s", {'shell_command': shell_command})

        ref = self._edge.api.execute("/config/device", "bgshell", shell_command)
        if not wait:
            return self._edge.tasks.awaitable_task(ref)
        try:
            task = self._edge.tasks.wait(ref)
            logger.info("Shell command executed. %s", {'shell_command': shell_command})
            return task.result.result
        except TaskException as error:
            raise CTERAException('An error occurred while executing Shell command.') from error
