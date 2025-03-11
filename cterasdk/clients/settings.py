import logging
import cterasdk.settings
from . import tracers
from ..common import Object


logger = logging.getLogger('cterasdk.http.trace')


class ClientSettings(Object):
    """
    Asynchronous HTTP Client Session Settings
    """

    def __init__(self, connector=None, timeout=None, cookie_jar=None):
        self.connector = connector if connector else TCPConnector(True)
        self.timeout = timeout if timeout else ClientTimeout(None, None)
        self.cookie_jar = cookie_jar if cookie_jar else CookieJar(False)
        self.trace_configs = [
            tracers.logger.trace_config(),
            tracers.session.trace_config()
        ]
        if cterasdk.settings.sessions.management.audit.postman.enabled:
            logger.info('Enabling Postman Auditing.')
            self.trace_configs.append(tracers.postman.trace_config())


class TCPConnector(Object):
    """
    Asynchronous HTTP TCP Connector
    """

    def __init__(self, ssl):
        self.ssl = ssl


class ClientTimeout(Object):
    """
    Asynchronous HTTP Client Timeout Settings
    """

    def __init__(self, sock_connect, sock_read):
        self.sock_connect = sock_connect
        self.sock_read = sock_read


class CookieJar(Object):
    """
    Asynchronous HTTP Cookie Jar Settings
    """

    def __init__(self, allow_unsafe):
        self.unsafe = allow_unsafe
