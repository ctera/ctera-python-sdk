import logging

from ..common import Object
from .base_command import BaseCommand


class Settings(BaseCommand):
    """
    CTERA Portal Settings APIs

    :ivar cterasdk.core.settings.GlobalSettings global_settings: Object holding the Portal Global Settings APIs
    """

    def __init__(self, core):
        super().__init__(core)
        self.global_settings = GlobalSettings(core)
        self.portal = PortalSettings(core)


class PortalSettings(BaseCommand):
    """
    Virtual Portal Settings APIs
    """
    def get(self):
        if self.session().in_tenant_context():
            return self._core.api.execute('', 'getSettings').settings
        return self._core.api.get('/settings/defaultPortalSettings')

    def use_global_settings(self):
        return self.update()

    def update(self, settings=None):
        """
        Update Portal Settings

        :param cterasdk.common.object.Objcet settings: Settings, defaults to using the global settings.
        """
        if not self.session().in_tenant_context():
            self._core.api.put('/settings/defaultPortalSettings', settings)
        else:
            param = PortalSettings._create_settings_parameter()
            if settings:
                param.fromSystem = False
                param.settings = settings
            self._core.api.execute('', 'setSettings', param)

    @staticmethod
    def _create_settings_parameter():
        param = Object()
        param._classname = 'SettingsParam'  # pylint: disable=protected-access
        param.fromSystem = True
        return param


class GlobalSettings(BaseCommand):
    """
    Global Settings APIs
    """

    def get_timezone(self):
        """
        Get timezone
        """
        return self._core.api.get('/settings/timezone')

    def set_timezone(self, timezone):
        """
        Set timezone

        :param str timezone: Timezone
        """
        logging.getLogger('cterasdk.core').info('Updating timezone. %s', {'timezone': timezone})
        response = self._core.api.put('/settings/timezone', timezone)
        logging.getLogger('cterasdk.core').info('Updated timezone. %s', {'timezone': timezone})
        return response
