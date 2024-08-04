import logging
from . import async_requests
from ..common import utils


class CookieJar:

    def __init__(self, cookies):
        self._cookies = cookies

    def get(self, key):
        return self._cookies.get(key)

    def update(self, cookies, response_url):
        self._cookies.update_cookies(cookies, response_url)


class PersistentHeaders:
    """Headers to include in every request"""

    def __init__(self):
        self._headers = {}

    @property
    def all(self):
        return self._headers

    def update_headers(self, headers):
        self._headers.update(headers)


class BaseClient:
    """Base Client"""

    def __init__(self, builder=None, async_session=None, authenticator=None, client_settings=None):
        """
        Initialize a Client

        :param builder: Endpoint builder.
        :param ,optional async_session: Re-use an asynchronous session.
        :param ,optional authenticator: Authenticator function.
        """
        self._headers = PersistentHeaders()
        self._authenticator = authenticator
        self._builder = builder
        self._client_settings = client_settings
        self._async_session = async_session if async_session else async_requests.Session(client_settings)

    @property
    def cookies(self):
        return CookieJar(self._async_session.cookies)

    @property
    def headers(self):
        return self._headers

    def join_headers(self, request):
        request.kwargs['headers'] = utils.merge(request.kwargs.get('headers', None), self.headers.all)
        return request

    @property
    def baseurl(self):
        return self._builder()

    def __str__(self):
        return f"({self.__class__.__name__} client at {hex(hash(self))}, baseurl={self.baseurl})"

    def _before_request(self):
        if self._async_session.closed:
            logging.getLogger('cterasdk.http').debug('Session Closed. Renewing.')
            self._async_session.initialize(self._client_settings)

    def request(self, request, *, on_response=None):
        self._before_request()
        return self._request(request, on_response=on_response)

    async def async_request(self, request, *, on_response=None):
        self._before_request()
        return await self._request(request, on_response=on_response)

    async def close(self):
        await self._async_session.close()


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
