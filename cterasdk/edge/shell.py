import logging

from . import taskmgr as TaskManager
from ..exception import CTERAException
from .base_command import BaseCommand


class Shell(BaseCommand):

    def run_command(self, shell_command):
        logging.getLogger().info("Executing shell command. %s", {'shell_command': shell_command})

        task = self._gateway.execute("/config/device", "bgshell", shell_command)
        try:
            task = TaskManager.wait(self._gateway, task)
            logging.getLogger().info("Shell command executed. %s", {'shell_command': shell_command})
            return task.result.result
        except TaskManager.TaskError as error:
            raise CTERAException('An error occurred while executing task', error)
