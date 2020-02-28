import logging

from .base_command import BaseCommand


class CLI(BaseCommand):
    """ Gateway CLI APIs """

    def run_command(self, cli_command):
        """
        Run a CLI command

        :param str cli_command: The CLI command to run on the gateway
        :return str: The response of the gateway
        """
        logging.getLogger().info("Executing CLI command. %s", {'cli_command': cli_command})

        response = self._gateway.execute('/config/device', 'debugCmd', cli_command)

        logging.getLogger().info("CLI command executed. %s", {'cli_command': cli_command})

        return response
