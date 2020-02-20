import logging


def run_cli_command(ctera_host, cli_command):
    logging.getLogger().info("Executing CLI command. %s", {'cli_command' : cli_command})

    response = ctera_host.execute('/config/device', 'debugCmd', cli_command)

    logging.getLogger().info("CLI command executed. %s", {'cli_command' : cli_command})

    return response
