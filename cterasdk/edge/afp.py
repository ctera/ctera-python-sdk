import logging

from .enum import Mode
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class AFP(BaseCommand):
    """ Edge Filer AFP APIs """

    def is_disabled(self):
        """ Check if the AFP server is disabled """
        return self._edge.api.get('/config/fileservices/afp/mode') == Mode.Disabled

    def disable(self):
        """
        Disable AFP
        """
        logger.info('Disabling AFP server.')
        self._edge.api.put('/config/fileservices/afp/mode', Mode.Disabled)
        logger.info('AFP server disabled.')
