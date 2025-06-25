import functools
import asyncio
import logging
import aiohttp

from yarl import URL


logger = logging.getLogger('cterasdk.http')


class Session:
    """Asynchronous HTTP Session"""

    def __init__(self, settings, trace):
        self._settings = settings
        self._trace = trace
        self._session = None

    @property
    def session(self):
        if self.closed:
            self._session = aiohttp.ClientSession(**self._settings, **self._trace)
        return self._session

    @property
    def cookies(self):
        return CookieJar(self.session.cookie_jar)

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
            raise
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


class CookieJar:

    def __init__(self, cookie_jar):
        self._cookie_jar = cookie_jar

    def update_cookies(self, cookies, response_url=None):
        self._cookie_jar.update_cookies(cookies, URL(response_url))

    def get(self, key):
        for cookie in self._cookie_jar:
            if cookie.key == key:
                return cookie.value
        return None

    def clear(self):
        self._cookie_jar.clear()


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
