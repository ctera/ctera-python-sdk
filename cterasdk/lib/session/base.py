import copy
from abc import abstractmethod

from .types import ConnectionStatus
from ...common import Object, Version
from ...exceptions import CTERAException


class BaseUser(Object):
    """Base User Account"""

    def __init__(self, name, domain=None):
        self.name = name
        self.domain = domain


class BaseSession(Object):
    """Base CTERA Session"""

    def __init__(self, address, product):
        """
        Initialize a Base Session Object

        :param str address: Hostname or IP address
        :param cterasdk.lib.session.types.Product product: Product
        """
        self.address = address
        self.product = product
        self.connection_status = ConnectionStatus.Disconnected
        self.account = None
        self.software_version = None

    def _before_session_start(self):
        self.connection_status = ConnectionStatus.Connecting

    def start_session(self, session):
        self._before_session_start()
        try:
            self._start_session(session)
            self._activate_connection()
        except CTERAException:
            self._deactivate_connection()
            raise

    @abstractmethod
    def _start_session(self, session):
        return NotImplementedError("Subclass must implement the '_start_session' method.")

    async def async_start_session(self, session):
        self._before_session_start()
        try:
            await self._async_start_session(session)
            self._activate_connection()
        except CTERAException:
            self._deactivate_connection()
            raise

    @abstractmethod
    async def _async_start_session(self, session):
        return NotImplementedError("Subclass must implement the '_start_session_async' method.")

    def _activate_connection(self):
        self._update_connection_status(ConnectionStatus.Connected)

    def stop_session(self):
        self._stop_session()
        self._deactivate_connection()

    def _deactivate_connection(self):
        self._update_connection_status(ConnectionStatus.Disconnected)
        self.account = None
        self.software_version = None

    def _update_account(self, account):
        self.account = account

    def _update_connection_status(self, connection_status):
        self.connection_status = connection_status

    def _update_software_version(self, software_version):
        self.software_version = Version(software_version)

    @property
    def connecting(self):
        return self.connection_status == ConnectionStatus.Connecting

    @property
    def connected(self):
        return self.connection_status == ConnectionStatus.Connected

    def whoami(self):
        session = copy.deepcopy(self)
        session.software_version = str(session.software_version) if session.software_version else None
        print(session)
