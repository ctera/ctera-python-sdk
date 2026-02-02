import functools
import asyncio
import logging
import aiohttp

from yarl import URL
from ..exceptions.transport import TLSError
from .settings import from_configuration

logger = logging.getLogger('cterasdk.http')


class Session:
    """Asynchronous HTTP Session"""

    def __init__(self, configuration):
        self._configuration = configuration
        self._cookie_jar = CachedCookieJar()
        self._session = None

    @property
    def session(self):
        if self.closed:
            self._session = aiohttp.ClientSession(**from_configuration(self._configuration))
            self._cookie_jar.register(self._session)
        self._cookie_jar.update_cookie_jar()
        return self._session

    @property
    def cookie_jar(self):
        return self._cookie_jar

    async def request(self, r, *, await_promise=False, on_response=None):
        if await_promise:
            return await self.await_promise(r, on_response=on_response)
        return await self.promise(r, on_response=on_response)

    async def promise(self, r, *, on_response=None):
        return await self._request(r, on_response=on_response)

    async def await_promise(self, r, *, on_response=None):
        promise = await self._request(r, on_response=on_response)
        return await promise

    async def _request(self, r, *, on_response=None):
        try:
            response = await self.session.request(r.method, r.url, **r.kwargs)
            return asyncio.create_task(on_response(response))
        except aiohttp.ClientSSLError as error:
            logger.warning(error)
            raise TLSError(error.host, error.port) from error
        except aiohttp.ClientProxyConnectionError as error:
            logger.warning(error)
            raise
        except aiohttp.ClientConnectorError as error:
            logger.warning(error)
            raise ConnectionError(error)
        except aiohttp.ServerDisconnectedError as error:
            logger.warning(error)
            raise ConnectionError(error)
        except asyncio.TimeoutError as error:
            logger.debug('Request timed out while making an HTTP request.')
            raise TimeoutError(error)

    @property
    def closed(self):
        return self._session.closed if self._session is not None else True

    async def close(self):
        if self._session is not None:
            await self._session.close()


def decorate_stream_error(stream_reader):
    @functools.wraps(stream_reader)
    async def wrapper(self, n=-1):
        try:
            return await stream_reader(self, n)
        except aiohttp.ClientPayloadError as error:
            logger.warning(error)
            raise IOError(error)
    return wrapper


class CachedCookieJar:

    def __init__(self):
        self._cache = {}
        self._session = None

    def register(self, session):
        self._session = session

    def ensure_session(func):
        def wrapper(self, *args, **kwargs):
            if self._session is not None and not self._session.closed:
                return func(self, *args, **kwargs)
            return None
        return wrapper

    @ensure_session
    def update_cookie_jar(self):
        for response_url, cookies in self._cache.items():
            self._session.cookie_jar.update_cookies(cookies, URL(response_url))
        self._cache.clear()

    def update_session(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.update_cookie_jar()
        return wrapper

    @update_session
    def update_cookies(self, cookies, response_url=None):
        logger.debug('Cookie update. Scope: %s', response_url)
        self._cache[response_url] = cookies

    @ensure_session
    def filter_cookies(self, response_url):
        return self._session.cookie_jar.filter_cookies(response_url)

    @ensure_session
    def get(self, response_url, key):
        """
        Get Cookie Value
        
        :param str response_url: URL
        :param str key: Cookie Key
        :returns: Cookie Value
        :rtype: str
        """
        cookies = self._session.cookie_jar.filter_cookies(response_url)
        cookie = cookies.get(key, None)
        return cookie.value if cookie else None

    @ensure_session
    def clear(self):
        return self._session.cookie_jar.clear()


class BaseRequest:
    """HTTP Request"""

    def __init__(self, method, url, **kwargs):
        self.method = method
        self.url = url
        self.kwargs = BaseRequest.accept(**kwargs)

    @staticmethod
    def accept(**kwargs):
        timeout = kwargs.get('timeout', None)
        if timeout:
            logger.debug('Setting request timeout. %s', timeout)
            kwargs['timeout'] = aiohttp.ClientTimeout(**timeout)
        return kwargs


class GetRequest(BaseRequest):
    """POST"""

    def __init__(self, url, **kwargs):
        super().__init__('GET', url, **kwargs)


class PutRequest(BaseRequest):
    """PUT"""

    def __init__(self, url, **kwargs):
        super().__init__('PUT', url, **kwargs)


class PostRequest(BaseRequest):
    """POST"""

    def __init__(self, url, **kwargs):
        super().__init__('POST', url, **kwargs)


class DeleteRequest(BaseRequest):
    """DELETE"""

    def __init__(self, url, **kwargs):
        super().__init__('DELETE', url, **kwargs)


class PropfindRequest(BaseRequest):
    """PROPFIND"""

    def __init__(self, url, **kwargs):
        super().__init__('PROPFIND', url, **kwargs)


class MkcolRequest(BaseRequest):
    """MKCOL"""

    def __init__(self, url, **kwargs):
        super().__init__('MKCOL', url, **kwargs)


class CopyRequest(BaseRequest):
    """COPY"""

    def __init__(self, url, **kwargs):
        super().__init__('COPY', url, **kwargs)


class MoveRequest(BaseRequest):
    """MOVE"""

    def __init__(self, url, **kwargs):
        super().__init__('MOVE', url, **kwargs)


class FormData(aiohttp.FormData):
    """Class representing URL-encoded form data"""
