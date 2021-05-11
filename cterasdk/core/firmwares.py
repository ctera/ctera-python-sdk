from .base_command import BaseCommand
from ..common import Object


class Firmwares(BaseCommand):
    """
    Portal Firmware Repository APIs
    """
    def list_images(self):
        """
        List Firmware Images.\n
        """
        if self.session().in_tenant_context():
            param = Object()
            param._classname = 'FirmwareParam'  # pylint: disable=protected-access
            return self._portal.execute('', 'getFirmwares', param)
        return self._portal.get('/firmwares')
