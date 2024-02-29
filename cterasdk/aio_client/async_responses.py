import asyncio
from ..convert import fromjsonstr, fromxmlstr


class Response:

    def __init__(self, response, deserializer=None):
        self._executor = asyncio.get_event_loop()
        self._response = response
        self._deserializer = deserializer

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

    def iter_content(self, chunk_size=None):
        while True:
            try:
                yield self._executor.run_until_complete(self._async_generator(chunk_size).__anext__())
            except StopAsyncIteration:
                break

    async def _async_generator(self, chunk_size=None):
        async for chunk in self._response.content.iter_chunked(chunk_size if chunk_size else 5120):
            yield chunk

    @property
    def text(self):
        return self._executor.run_until_complete(contents()(self._response))

    def deserialize(self):
        return self._executor.run_until_complete(self._deserializer(self._response)) if self._deserializer else self.text

    @staticmethod
    def new(deserializer=None):
        async def new_response(response):
            return Response(response, deserializer)
        return new_response


def contents():
    async def text(response):
        return await response.text()
    return text


def deserialize_object(deserializer):
    async def deserialize(response):
        return deserializer(await response.read())
    return deserialize


class Deserializers:
    JSON = deserialize_object(fromjsonstr)
    XML = deserialize_object(fromxmlstr)
