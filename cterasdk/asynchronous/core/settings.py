import logging
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


class Settings(BaseCommand):
    """
    CTERA Portal Settings APIs

    :ivar cterasdk.asynchronous.core.settings.GlobalSettings global_settings: Object holding the Portal Global Settings APIs
    """

    def __init__(self, core):
        super().__init__(core)
        self.global_settings = GlobalSettings(core)


class GlobalSettings(BaseCommand):
    """
    Global Settings APIs
    """

    @property
    async def dns_suffix(self):
        return await self._core.v1.api.get('/settings/dnsSuffix')
