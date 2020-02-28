import logging
from .base_command import BaseCommand


class Timezone(BaseCommand):
    """ Gateway Timezone configuration """

    def set_timezone(self, timezone):
        """
        Set Timezone

        :param str timezone: New timezone to set
        """
        logging.getLogger().info("Updating timezone. %s", {'timezone': timezone})

        self._gateway.put('/config/time/TimeZone', timezone)

        logging.getLogger().info("Timezone updated. %s", {'timezone': timezone})
