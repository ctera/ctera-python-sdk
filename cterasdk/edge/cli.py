import logging

from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class CLI(BaseCommand):
    """ CLI APIs """

    def run_command(self, cli_command):
        """
        Run a CLI command

        :param str cli_command: Command
        :return str: Response
        """
        logger.warning('Usage of the CLI module is discouraged. '
                       'Review available modules to determine if there are existing ones that '
                       'support this action.')
        logger.info("Executing CLI command. %s", {'cli_command': cli_command})
        response = self._edge.api.execute('/config/device', 'debugCmd', cli_command)
        logger.info("CLI command executed. %s", {'cli_command': cli_command})
        return response
