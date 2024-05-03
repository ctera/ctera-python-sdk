import logging

from .enum import Mode
from .base_command import BaseCommand


class AFP(BaseCommand):
    """ Edge Filer AFP APIs """

    def is_disabled(self):
        """ Check if the AFP server is disabled """
        return self._edge.api.get('/config/fileservices/afp/mode') == Mode.Disabled

    def disable(self):
        """
        Disable AFP
        """
        logging.getLogger('cterasdk.edge').info('Disabling AFP server.')

        self._edge.api.put('/config/fileservices/afp/mode', Mode.Disabled)

        logging.getLogger('cterasdk.edge').info('AFP server disabled.')
