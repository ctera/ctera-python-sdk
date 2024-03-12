import asyncio
import logging
import aiohttp

from yarl import URL
from . import async_tracers


def create_connector(**kwargs):
    return aiohttp.TCPConnector(**kwargs)


def create_cookie_jar(**kwargs):
    return aiohttp.CookieJar(**kwargs)


class Session:
    """Asynchronous HTTP Session"""

    def __init__(self, **kwargs):
        self._session = aiohttp.ClientSession(trace_configs=[async_tracers.default()], **kwargs)

    @property
    def cookies(self):
        return CookieJar(self._session.cookie_jar)

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
            response = await self._session.request(r.method, r.url, **r.kwargs)
            return asyncio.create_task(on_response(response))
        except aiohttp.ClientSSLError as error:
            logging.getLogger().warning(error)
            raise
        except aiohttp.ClientProxyConnectionError as error:
            logging.getLogger().error(error)
            raise
        except aiohttp.ClientConnectorError as error:
            logging.getLogger().error(error)
            raise ConnectionError(error)
        except aiohttp.ServerDisconnectedError as error:
            logging.getLogger().error(error)
            raise ConnectionError(error)
        except asyncio.TimeoutError as error:
            logging.getLogger().error('Request timed out while making an HTTP request.')
            raise TimeoutError(error)

    @staticmethod
    def new(**kwargs):
        return Session(**kwargs)

    async def shutdown(self):
        await self._session.close()


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


class BaseRequest:
    """HTTP Request"""

    def __init__(self, method, url, **kwargs):
        self.method = method
        self.url = url
        self.kwargs = kwargs


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
