import logging
from .enum import Mode
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Antivirus(BaseCommand):
    """Edge Filer Antivirus APIs"""

    def __init__(self, edge):
        super().__init__(edge)
        self.settings = Settings(self._edge)

    def enable(self):
        """
        Enable Bit Defender antivirus.
        """
        logger.info('Enabling antivirus.')
        response = self._edge.api.put('/config/av/realtime/mode', Mode.Enabled)
        logger.info('Antivirus enabled.')
        return response

    def disable(self):
        """
        Disable Bit Defender antivirus.
        """
        logger.info('Disabling antivirus.')
        response = self._edge.api.put('/config/av/realtime/mode', Mode.Disabled)
        logger.info('Antivirus disabled.')
        return response

    def update(self):
        """
        Check for updates.
        """
        return self._edge.api.execute('/config/av/updates', 'updatenow')

    def status(self):
        """
        Get Status.
        """
        return self._edge.api.get('/status/av')


class Settings(BaseCommand):

    def get(self):
        """
        Get antivirus settings.
        """
        return self._edge.api.get('/config/av/updates')

    def update(self, schedule, disabled=False):
        """
        Update antivirus settings.

        :param cterasdk.edge.types.AntivirusUpdateSchedule schedule: Antivirus update schedule
        :param bool,optional disabled: Enable or disable automatic updates, defaults to ``False``
        """
        settings = self.get()
        settings.mode = Mode.Disabled if disabled is True else Mode.Enabled
        settings.schedule = schedule
        return self._edge.api.put('/config/av/updates', settings)
