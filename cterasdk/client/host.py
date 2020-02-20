import logging
import socket

from ..common import Object
from ..convert import tojsonstr
from ..exception import HostUnreachable
from .cteraclient import CTERAClient


class NetworkHost:
    def __init__(self, host, port, https):
        self._host = host
        self._port = port
        self._https = https

    def test_conn(self):
        logging.getLogger().debug('Testing connection. %s', {'host' : self.host(), 'port' : self.port()})
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rc = None
        try:
            rc = sock.connect_ex((self._host, self._port))
        except socket.gaierror:
            logging.getLogger().debug('Host unreachable. %s', {'host' : self.host(), 'port' : self.port()})
            raise HostUnreachable(None, self._host, self._port, self.scheme().upper())

        if rc != 0:
            logging.getLogger().debug('Host unreachable. %s', {'host' : self.host(), 'port' : self.port()})
            raise HostUnreachable(None, self._host, self._port, self.scheme().upper())

        logging.getLogger().debug('Host is reachable. %s', {'host' : self.host(), 'port' : self.port()})

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
        x.__dict__ = {k : v for k, v in self.__dict__.items() if not k.startswith('_')}
        return tojsonstr(x)


class CTERAHost(NetworkHost):

    def __init__(self, host, port, https):
        super(CTERAHost, self).__init__(host, port, https)
        self._ctera_client = CTERAClient()
        self._session = None

    def session(self):
        return self._session

    def register_session(self, session):
        self._session = session

    def get(self, baseurl, path, params):
        return self._ctera_client.get(baseurl, path, params)

    def openfile(self, baseurl, path, params):
        return self._ctera_client.download(baseurl, path, params)

    def show(self, baseurl, path):
        print(tojsonstr(CTERAHost.get(self, baseurl, path, params={})))

    def get_multi(self, baseurl, path, paths):
        return self._ctera_client.get_multi(baseurl, path, paths)

    def show_multi(self, baseurl, path, paths):
        print(tojsonstr(self.get_multi(baseurl, path, paths)))

    def put(self, baseurl, path, value):
        response = self._ctera_client.put(baseurl, path, value)
        logging.getLogger().debug('Configuration changed. %s', {'url': path, 'value': value})
        return response

    def post(self, baseurl, path, value):
        response = self._ctera_client.post(baseurl, path, value)
        logging.getLogger().debug('Added. %s', {'url': path, 'value': value})
        return response

    def form_data(self, baseurl, path, form_data):

        return self._ctera_client.form_data(baseurl, path, form_data)

    def db(self, baseurl, path, name, param):
        response = self._ctera_client.db(baseurl, path, name, param)
        logging.getLogger().debug('Database method executed. %s', {'url': path, 'name': name, 'param': param})
        return response

    def execute(self, baseurl, path, name, param):
        response = self._ctera_client.execute(baseurl, path, name, param)
        logging.getLogger().debug('User-defined method executed. %s', {'url': path, 'name': name, 'param': param})
        return response

    def add(self, baseurl, path, param):
        return self.db(baseurl, path, 'add', param)

    def delete(self, baseurl, path):
        response = self._ctera_client.delete(baseurl, path)
        logging.getLogger().debug('Deleted. %s', {'url' : path})
        return response

    def mkcol(self, baseurl, path):
        return self._ctera_client.mkcol(baseurl, path)
