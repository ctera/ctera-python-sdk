from abc import ABC, abstractmethod
from contextlib import contextmanager
from ..exceptions.transport import HTTPError


class RemoteCommand(ABC):
    """Command on a Remote Resource"""

    def __enter__(self):
        return self.execute()

    async def __aenter__(self):
        return await self.a_execute()

    def __init__(self, function, receiver):
        self._classname = self.__class__.__name__
        self._function = function
        self._receiver = receiver

    def _before_command(self):
        """Override '_before_command"""

    @contextmanager
    def trace_execution(self):
        self._before_command()
        yield
        self._after_command()

    def get_parameter(self):
        raise NotImplementedError("Subclass must implement the 'get_parameter' method.")

    def execute(self):
        try:
            r = self._execute()
            return self._handle_response(r)
        except HTTPError as e:
            return self._handle_exception(e)

    @abstractmethod
    def _execute(self):
        raise NotImplementedError("Subclass must implement the '_execute' method.")

    async def a_execute(self):
        try:
            r = await self._a_execute()
            return self._handle_response(r)
        except HTTPError as e:
            return self._handle_exception(e)

    @abstractmethod
    async def _a_execute(self):
        raise NotImplementedError("Subclass must implement the '_a_execute' method.")

    def _handle_response(self, r):  # pylint: disable=no-self-use
        """
        Override this method to handle the response.
        """
        return r

    def _handle_exception(self, e):  # pylint: disable=no-self-use
        """
        Override this method to handle exceptions.
        """
        raise e

    def _after_command(self):
        """Override '_after_command'"""

    def __exit__(self, exc_type, exc, tb):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        pass


class PortalCommand(RemoteCommand):
    """Abstract Portal Command"""


class EdgeCommand(RemoteCommand):
    """Abstract Edge Command"""
