from ..base import BaseClient, BaseResponse
from ..common import Serializers, Deserializers
from .. import async_requests, decorators


class AsyncClient(BaseClient):
    """Asynchronous Client"""

    @decorators.authenticated
    async def get(self, path, data, *, on_response=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return await self._request(request, on_response=on_response)

    @decorators.authenticated
    async def put(self, path, data, *, data_serializer=None, on_response=None, **kwargs):
        request = async_requests.PutRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return await self._request(request, on_response=on_response)

    @decorators.authenticated
    async def post(self, path, data, *, data_serializer=None, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return await self._request(request, on_response=on_response)

    @decorators.authenticated
    async def form_data(self, path, data, *, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=Serializers.FormData(data), **kwargs)
        return await self._request(request, on_response=on_response)

    @decorators.authenticated
    async def delete(self, path, *, on_response=None, **kwargs):
        request = async_requests.DeleteRequest(self._builder(path), **kwargs)
        return await self._request(request, on_response=on_response)

    async def _request(self, request, *, on_response=None):
        on_response = on_response if on_response else AsyncResponse.new()
        return await self._async_session.await_promise(request, on_response=on_response)


class AsyncJSON(AsyncClient):

    async def put(self, path, data, **kwargs):
        return await super().put(path, data, data_serializer=Serializers.JSON, **kwargs)

    async def post(self, path, data, **kwargs):
        return await super().post(path, data, data_serializer=Serializers.JSON, **kwargs)


class AsyncXML(AsyncClient):

    async def put(self, path, data, **kwargs):
        return await super().put(path, data, data_serializer=Serializers.XML, **kwargs)

    async def post(self, path, data, **kwargs):
        return await super().post(path, data, data_serializer=Serializers.XML, **kwargs)


class AsyncResponse(BaseResponse):
    """Asynchronous Response Object"""

    async def chunk(self, chunk_size=None):
        async for chunk in self._response.content.iter_chunked(chunk_size if chunk_size else 5120):
            yield chunk

    async def text(self):
        return await self._response.text()

    async def json(self):
        return Deserializers.JSON(await self._response.read())

    async def xml(self):
        return Deserializers.XML(await self._response.read())
