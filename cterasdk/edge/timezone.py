import logging
from .base_command import BaseCommand


class Timezone(BaseCommand):
    """ Edge Filer Timezone configuration """

    def get_timezone(self):
        """
        Get the timezone of the Edge Filer

        :return str: The timezone of the Edge Filer
        """
        return self._edge.api.get('/config/time/TimeZone')

    def set_timezone(self, timezone):
        """
        Set Timezone

        :param str timezone: New timezone to set
        """
        logging.getLogger('cterasdk.edge').info("Updating timezone. %s", {'timezone': timezone})

        self._edge.api.put('/config/time/TimeZone', timezone)

        logging.getLogger('cterasdk.edge').info("Timezone updated. %s", {'timezone': timezone})
