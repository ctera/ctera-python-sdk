import logging

from .base_command import BaseCommand


class CLI(BaseCommand):

    def run_command(self, cli_command):
        logging.getLogger().info("Executing CLI command. %s", {'cli_command': cli_command})

        response = self._gateway.execute('/config/device', 'debugCmd', cli_command)

        logging.getLogger().info("CLI command executed. %s", {'cli_command': cli_command})

        return response
