from abc import abstractmethod

import cterasdk.settings
from . import endpoints, uri
from .utils import URI
from ..clients.settings import ClientSettings, ClientTimeout, TCPConnector, CookieJar
from ..clients.synchronous import clients
from ..common import Object
from ..convert import tojsonstr


class Service:

    def __init__(self, host, port, https, base):
        self._base = base if base else str(URI.instance(f'http{"s" if https else ""}', host, port or 443 if https else 80))

    @property
    def base(self):
        return self._base

    def host(self):
        hostname = uri.components(self._base).hostname
        return hostname if hostname else ''

    def port(self):
        components = uri.components(self._base)
        return components.port or 443 if components.scheme == 'https' else 80

    @property
    def _omit_fields(self):
        return []

    def __str__(self):
        x = Object()
        x.__dict__ = {k: v for k, v in self.__dict__.items() if not (k.startswith('_') or k in self._omit_fields)}
        return tojsonstr(x)


class CTERA(Service):

    def __init__(self, host, port, https, base):
        super().__init__(host, port, https, base)
        self._ctera_session = None
        self._ctera_clients = None

    @property
    def clients(self):
        return self._ctera_clients

    def session(self):
        return self._ctera_session

    def _before_login(self):
        """Override to implement logic before login"""

    def _after_login(self):
        """Override to implement logic after login"""

    @property
    @abstractmethod
    def _login_object(self):
        raise NotImplementedError(
            "Implementing class must implement the login_object property by returning an object with login and logout methods"
        )

    @abstractmethod
    def _authenticator(self, url):
        raise NotImplementedError("Subclass must implement the '_authenticator' function")

    def whoami(self):
        """
        Return the name of the logged in user.

        :return cterasdk.common.object.Object: The session object of the current user
        """
        return self._ctera_session.whoami()


def client_settings(parameters):
    return ClientSettings(
        TCPConnector(parameters.ssl),
        ClientTimeout(**parameters.timeout.kwargs),
        CookieJar(parameters.allow_unsafe)
    )


class Management(CTERA):

    def __enter__(self):
        return self

    def __init__(self, host, port, https, base):
        super().__init__(host, port, https, base)
        self._default = clients.Client(endpoints.EndpointBuilder.new(self.base),
                                       settings=client_settings(cterasdk.settings.sessions.management),
                                       authenticator=self._authenticator)

    def login(self, username, password):
        """
        Log in

        :param str username: Username
        :param str password: Password
        """
        self._before_login()
        self._login_object.login(username, password)
        self._ctera_session.start_session(self)
        self._after_login()

    def logout(self):
        """ Log out """
        if self._ctera_session.connected:
            self._login_object.logout()
            self._ctera_session.stop_session()
        self._default.close()

    @abstractmethod
    def test(self):
        return NotImplementedError("Subclass must implement the 'test' function")

    @property
    @abstractmethod
    def _session_id_key(self):
        return NotImplementedError("Subclass must implement the '_session_id_key' property")

    @property
    def default(self):
        return self._default

    def get_session_id(self):
        """
        Get Session Identifier

        :return str: Session ID
        """
        return self._default.cookies.get(self._session_id_key)

    def set_session_id(self, session_id):
        self._default.cookies.update({self._session_id_key: session_id}, self._default.baseurl)
        self._ctera_session.start_session(self)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._default.close()
