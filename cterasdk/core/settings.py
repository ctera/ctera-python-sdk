import logging

from .base_command import BaseCommand


class Settings(BaseCommand):
    """
    Portal Settings APIs

    :ivar cterasdk.core.settings.GlobalSettings global_settings: Object holding the Portal Global Settings APIs
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.global_settings = GlobalSettings(self._portal)


class GlobalSettings(BaseCommand):

    def get_timezone(self):
        """
        Get timezone
        """
        return self._portal.get('/settings/timezone')

    def set_timezone(self, timezone):
        """
        Set timezone

        :param str timezone: Timezone
        """
        logging.getLogger().info('Updating timezone. %s', {'timezone': timezone})
        response = self._portal.put('/settings/timezone', timezone)
        logging.getLogger().info('Updated timezone. %s', {'timezone': timezone})
        return response
