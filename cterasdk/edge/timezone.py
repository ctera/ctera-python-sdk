import logging
from .base_command import BaseCommand


class Timezone(BaseCommand):

    def set_timezone(self, timezone):
        logging.getLogger().info("Updating timezone. %s", {'timezone': timezone})

        self._gateway.put('/config/time/TimeZone', timezone)

        logging.getLogger().info("Timezone updated. %s", {'timezone': timezone})
