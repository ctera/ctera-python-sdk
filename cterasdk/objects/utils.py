import urllib.parse
from ..common import Object


class URI:
    """A Class Representing a URI"""

    def __init__(self, uri):
        self._uri = urllib.parse.urlparse(uri)

    @property
    def scheme(self):
        return self._uri.scheme

    @property
    def host(self):
        return self._uri.hostname

    @property
    def port(self):
        return self._uri.port or 443

    @property
    def netloc(self):
        return self._uri.netloc

    @property
    def path(self):
        return self._uri.path

    def to_server_object(self):
        param = Object()
        param.scheme = self.scheme
        param.netloc = self.netloc
        param.host = self.host
        param.port = self.port
        param.path = self.path
        param.uri = str(self)
        return param

    @staticmethod
    def instance(scheme, host, port=None, path=None, query=None):
        """
        Create a URI from a list of arguments

        :param str host: Host
        :param int,optional port: Port
        :param str,optional path: Path
        :param dict[str],optional query: Query string parameters
        """
        query = '&'.join([f"{k}={v}" for k, v in query.items()]) if query else ''
        netloc = f"{host}" + (f":{port}" if port else '')
        return URI(urllib.parse.urlunparse(
            (scheme, netloc, path if path else '', '', query, '')
        ))

    def __str__(self):
        return self._uri.geturl()
