import logging
from .base import BaseSession, BaseUser
from .types import Product

from ...common import Object


class Connection(Object):
    """Connection"""

    def __init__(self, remote, source=None):
        self.remote = remote
        if source:
            self.source = source


class LocalUser(BaseUser):
    """Local User"""


class RemoteUser(BaseUser):
    """Remote User"""

    def __init__(self, name, domain, tenant):
        super().__init__(name, domain)
        self.tenant = tenant


class Session(BaseSession):

    def __init__(self, address):
        super().__init__(address, Product.Edge)
        self.connection = None

    def _start_session(self, session):
        logging.getLogger('cterasdk.edge').debug('Starting Session.')
        username = session.api.get('/currentuser').username
        software_version = session.api.get('/status/device/runningFirmware')
        self._update_session(username, software_version)

    async def _async_start_session(self, session):
        logging.getLogger('cterasdk.edge').debug('Starting Session.')
        user = session.api.get('/currentuser')
        software = session.api.get('/status/device/runningFirmware')
        self._update_session((await user).username, await software)

    def _update_session(self, username, software_version):
        self._update_account(LocalUser(username))
        self._update_software_version(software_version)
        self.connection = Connection(False)

    def start_remote_session(self, session):
        logging.getLogger('cterasdk.edge').debug('Starting Remote Session.')
        self._update_account(RemoteUser(session.account.name, session.account.domain, session.account.tenant))
        self.connection = Connection(True, session.address)

    def _stop_session(self):
        logging.getLogger('cterasdk.edge').debug('Stopping Session.')
        self.connection = None
