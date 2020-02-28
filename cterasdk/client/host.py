import functools
import logging
import socket

from ..common import Object
from ..convert import tojsonstr
from ..exception import HostUnreachable
from .cteraclient import CTERAClient
from ..exception import CTERAException


def authenticated(function):
    @functools.wraps(function)
    def check_authenticated_and_call(self, *args, **kwargs):
        if self._is_authenticated(function, *args, **kwargs):  # pylint: disable=protected-access
            return function(self, *args, **kwargs)
        logging.getLogger().error('Not logged in.')
        raise CTERAException('Not logged in')

    return check_authenticated_and_call


class NetworkHost:
    def __init__(self, host, port, https):
        self._host = host
        self._port = port
        self._https = https

    @property
    def _omit_fields(self):
        return []

    def test_conn(self):
        logging.getLogger().debug('Testing connection. %s', {'host': self.host(), 'port': self.port()})
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rc = None
        try:
            rc = sock.connect_ex((self._host, self._port))
        except socket.gaierror:
            logging.getLogger().debug('Host unreachable. %s', {'host': self.host(), 'port': self.port()})
            raise HostUnreachable(None, self._host, self._port, self.scheme().upper())

        if rc != 0:
            logging.getLogger().debug('Host unreachable. %s', {'host': self.host(), 'port': self.port()})
            raise HostUnreachable(None, self._host, self._port, self.scheme().upper())

        logging.getLogger().debug('Host is reachable. %s', {'host': self.host(), 'port': self.port()})

    def scheme(self):
        return 'http' + ("s" if self._https else '')

    def host(self):
        return self._host

    def port(self):
        return self._port

    def https(self):
        return self._https

    def baseurl(self):
        return 'http' + ("s" if self._https else '') + '://' + self._host + ':' + str(self._port)

    def __str__(self):
        x = Object()
        x.__dict__ = {k: v for k, v in self.__dict__.items() if not (k.startswith('_') or k in self._omit_fields)}
        return tojsonstr(x)


class CTERAHost(NetworkHost):

    def __init__(self, host, port, https):
        super().__init__(host, port, https)
        self._ctera_client = CTERAClient()
        self._session = None
        self.login = self._login_object.login
        self.logout = self._login_object.logout

    @property
    def _omit_fields(self):
        return super()._omit_fields + [
            'login',
            'logout'
        ]

    @property
    def base_api_url(self):
        raise NotImplementedError("Implementing class must implement the base_api_url property")

    @property
    def base_file_url(self):
        raise NotImplementedError("Implementing class must implement the base_api_url property")

    @property
    def _login_object(self):
        raise NotImplementedError(
            "Implementing class must implement the login_object property by returning an object with login and logout methods"
        )

    def _is_authenticated(self, function, *args, **kwargs):
        raise NotImplementedError("Implementing class must implement the _is_authenticated method")

    def session(self):
        return self._session

    def register_session(self, session):
        self._session = session

    @authenticated
    def get(self, path, params=None, use_file_url=False):
        return self._ctera_client.get(self.base_file_url if use_file_url else self.base_api_url, path, params or {})

    @authenticated
    def openfile(self, path, params=None, use_file_url=False):
        return self._ctera_client.download(self.base_file_url if use_file_url else self.base_api_url, path, params or {})

    @authenticated
    def show(self, path, use_file_url=False):
        print(tojsonstr(self.get(path, params={}, use_file_url=use_file_url)))

    @authenticated
    def get_multi(self, path, paths, use_file_url=False):
        return self._ctera_client.get_multi(self.base_file_url if use_file_url else self.base_api_url, path, paths)

    @authenticated
    def show_multi(self, path, paths, use_file_url=False):
        print(tojsonstr(self.get_multi(path, paths, use_file_url=use_file_url)))

    @authenticated
    def put(self, path, value, use_file_url=False):
        response = self._ctera_client.put(self.base_file_url if use_file_url else self.base_api_url, path, value)
        logging.getLogger().debug('Configuration changed. %s', {'url': path, 'value': value})
        return response

    @authenticated
    def post(self, path, value, use_file_url=False):
        response = self._ctera_client.post(self.base_file_url if use_file_url else self.base_api_url, path, value)
        logging.getLogger().debug('Added. %s', {'url': path, 'value': value})
        return response

    def form_data(self, path, form_data, use_file_url=False):
        return self._ctera_client.form_data(self.base_file_url if use_file_url else self.base_api_url, path, form_data)

    @authenticated
    def db(self, path, name, param, use_file_url=False):
        response = self._ctera_client.db(self.base_file_url if use_file_url else self.base_api_url, path, name, param)
        logging.getLogger().debug('Database method executed. %s', {'url': path, 'name': name, 'param': param})
        return response

    @authenticated
    def execute(self, path, name, param=None, use_file_url=False):
        response = self._ctera_client.execute(self.base_file_url if use_file_url else self.base_api_url, path, name, param)
        logging.getLogger().debug('User-defined method executed. %s', {'url': path, 'name': name, 'param': param})
        return response

    @authenticated
    def add(self, path, param, use_file_url=False):
        return self.db(path, 'add', param, use_file_url=use_file_url)

    @authenticated
    def delete(self, path, use_file_url=False):
        response = self._ctera_client.delete(self.base_file_url if use_file_url else self.base_api_url, path)
        logging.getLogger().debug('Deleted. %s', {'url': path})
        return response

    @authenticated
    def mkcol(self, path, use_file_url=False):
        return self._ctera_client.mkcol(self.base_file_url if use_file_url else self.base_api_url, path)

    def whoami(self):
        return self._session.whoami()
