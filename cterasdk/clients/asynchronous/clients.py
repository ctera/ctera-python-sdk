from . import errors
from ..base import BaseClient, BaseResponse
from ..common import Serializers, Deserializers
from .. import async_requests, decorators
from ...common import Object


class AsyncClient(BaseClient):
    """Asynchronous Client"""

    @decorators.authenticated
    async def get(self, path, *, on_response=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return await self.async_request(request, on_response=on_response)

    @decorators.authenticated
    async def put(self, path, data, *, data_serializer=None, on_response=None, **kwargs):
        request = async_requests.PutRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return await self.async_request(request, on_response=on_response)

    @decorators.authenticated
    async def post(self, path, data, *, data_serializer=None, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return await self.async_request(request, on_response=on_response)

    @decorators.authenticated
    async def form_data(self, path, data, *, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=Serializers.FormData(data), **kwargs)
        return await self.async_request(request, on_response=on_response)

    @decorators.authenticated
    async def delete(self, path, *, on_response=None, **kwargs):
        request = async_requests.DeleteRequest(self._builder(path), **kwargs)
        return await self.async_request(request, on_response=on_response)

    async def _request(self, request, *, on_response=None):
        on_response = on_response if on_response else AsyncResponse.new()
        response = await self._async_session.await_promise(self.join_headers(request), on_response=on_response)
        return await errors.accept(response)


class AsyncWebDAV(AsyncClient):
    """WebDAV"""


class AsyncJSON(AsyncClient):

    def __init__(self, builder=None, async_session=None, authenticator=None, client_settings=None):
        super().__init__(builder, async_session, authenticator, client_settings)
        self.headers.update_headers({'Content-Type': 'application/json'})

    async def get(self, path, **kwargs):
        response = await super().get(path, **kwargs)
        return await response.json()

    async def put(self, path, data, **kwargs):
        response = await super().put(path, data, data_serializer=Serializers.JSON, **kwargs)
        return await response.json()

    async def post(self, path, data, **kwargs):
        response = await super().post(path, data, data_serializer=Serializers.JSON, **kwargs)
        return await response.json()

    async def delete(self, path, **kwargs):
        response = await super().delete(path, **kwargs)
        return await response.json()


class AsyncXML(AsyncClient):

    async def get(self, path, **kwargs):
        response = await super().get(path, **kwargs)
        return await response.xml()

    async def put(self, path, data, **kwargs):
        response = await super().put(path, data, data_serializer=Serializers.XML, **kwargs)
        return await response.xml()

    async def post(self, path, data, **kwargs):
        response = await super().post(path, data, data_serializer=Serializers.XML, **kwargs)
        return await response.xml()

    async def delete(self, path, **kwargs):
        response = await super().delete(path, **kwargs)
        return await response.xml()


class AsyncExtended(AsyncXML):
    """CTERA Schema"""

    async def get_multi(self, path, paths):
        return await self.database(path, 'get-multi', paths)

    async def execute(self, path, name, param=None):  # schema method
        return await self._execute(path, 'user-defined', name, param)

    async def database(self, path, name, param=None):  # schema method
        return await self._execute(path, 'db', name, param)

    async def _execute(self, path, _type, name, param):
        data = Object()
        data.type = _type
        data.name = name
        data.param = param
        return await super().post(path, data)


class AsyncAPI(AsyncExtended):
    """CTERA Management API"""


class AsyncResponse(BaseResponse):
    """Asynchronous Response Object"""

    async def async_iter_content(self, chunk_size=None):
        async for chunk in self._response.content.iter_chunked(chunk_size if chunk_size else 5120):
            yield chunk

    async def text(self):
        return await self._response.text()

    async def json(self):
        return Deserializers.JSON(await self._response.read())

    async def xml(self):
        return Deserializers.XML(await self._response.read())

    async def read(self, n=-1):
        return await self._response.content.read(n)

    @staticmethod
    def new():
        async def new_response(response):
            return AsyncResponse(response)
        return new_response
