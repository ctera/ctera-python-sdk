import logging

from .base_command import BaseCommand


class CLI(BaseCommand):
    """ Portal CLI APIs """

    def run_command(self, cli_command):
        """
        Run a CLI command

        :param str cli_command: The CLI command to run on the gateway
        :return str: The response of the Portal
        """
        logging.getLogger('cterasdk.core').warning('Usage of the CLI module is discouraged. '
                                                   'Review available modules to determine if there are existing ones that '
                                                   'support this action.')
        logging.getLogger('cterasdk.core').info("Executing CLI command. %s", {'cli_command': cli_command})
        response = self._core.api.execute('', 'debugCmd', cli_command)
        logging.getLogger('cterasdk.core').info("CLI command executed. %s", {'cli_command': cli_command})
        return response
