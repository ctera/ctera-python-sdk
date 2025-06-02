import logging
import threading
from . import async_requests, errors
from .settings import ClientSessionSettings, TraceSettings
from ..common import utils


logger = logging.getLogger('cterasdk.http')


class CookieJar:

    def __init__(self, cookies):
        self._cookies = cookies

    def get(self, key):
        return self._cookies.get(key)

    def update(self, cookies, response_url):
        self._cookies.update_cookies(cookies, response_url)

    def clear(self):
        self._cookies.clear()


class PersistentHeaders:
    """Headers to include in every request"""

    def __init__(self):
        self._headers = {}

    @property
    def all(self):
        return self._headers

    def persist_response_header(self, response, header):
        """
        Persist header from response object.

        :param cterasdk.clients.base.BaseResponse response: Response object
        :param str header: Header name
        """
        value = response.headers.get(header, None)
        if value:
            self.persist_headers({header: value})
        else:
            logger.debug("Could not find header: '%s' in response", header)

    def persist_headers(self, headers):
        self._headers.update(headers)


class BaseClient:
    """Base Client"""

    def __init__(self, builder=None, session=None, settings=None, authenticator=None):
        """
        Initialize a Client

        :param builder: Endpoint builder.
        :param ,optional session: Session.
        :param ,optional settings: Client Session Settings.
        :param ,optional authenticator: Authenticator function.
        """
        self._headers = PersistentHeaders()
        self._authenticator = authenticator
        self._builder = builder

        default_settings = ClientSessionSettings()
        if settings:
            default_settings.update(**settings)

        self._session = session if session else async_requests.Session(default_settings, TraceSettings())

    def clone(self, definition, builder=None, authenticator=None):
        """
        Clone a Client

        :param class definition: Class definition.
        :param ,optional builder: Endpoint builder.
        :param ,optional authenticator: Authenticator function.
        """
        return definition(
            builder if builder is not None else self._builder,
            self._session,
            None,
            authenticator if authenticator is not None else self._authenticator,
        )

    @property
    def cookies(self):
        return CookieJar(self._session.cookies)

    @property
    def headers(self):
        return self._headers

    def join_headers(self, request):
        request.kwargs['headers'] = utils.merge(request.kwargs.get('headers', None), self.headers.all)
        return request

    @property
    def baseurl(self):
        return self._builder()

    def request(self, request, *, on_response=None, on_error=None):
        on_error = on_error if on_error else errors.DefaultHandler()
        return self._request(request, on_response=on_response, on_error=on_error)

    async def a_request(self, request, *, on_response=None, on_error=None):
        on_error = on_error if on_error else errors.DefaultHandler()
        return await self._request(request, on_response=on_response, on_error=on_error)

    async def close(self):
        await self._session.close()

    def __str__(self):
        return f"({self.__class__.__name__} client at {hex(hash(self))}, baseurl={self.baseurl})"


class BaseResponse:
    """Base Response Object"""

    def __init__(self, response):
        self._response = response

    @property
    def method(self):
        return self._response.method

    @property
    def ok(self):
        return self._response.ok

    @property
    def reason(self):
        return self._response.reason

    @property
    def url(self):
        return self._response.url

    @property
    def real_url(self):
        return self._response.real_url

    @property
    def status(self):
        return self._response.status

    @property
    def headers(self):
        return self._response.headers

    def raise_for_status(self):
        return self._response.raise_for_status()


def run_threadsafe(loop, target, *args, **kwargs):
    event = threading.Event()

    t = Task(loop, event, target, *args, **kwargs)
    t.start()

    event.wait()

    if t.exception:
        raise t.exception
    return t.response


class Task(threading.Thread):

    def __init__(self, loop, event, target, *args, **kwargs):
        super().__init__(name='Thread-safe Executor')
        self.loop = loop
        self.event = event
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.exception = None
        self.response = None

    def run(self):
        try:
            self.response = self.loop.run_until_complete(self.target(*self.args, **self.kwargs))
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.exception = e
        finally:
            self.event.set()
