import asyncio
from .errors import XMLHandler, JSONHandler
from .base import BaseClient, BaseResponse, run_threadsafe
from .common import Serializers, Deserializers
from . import async_requests, decorators
from ..common import Object


class AsyncClient(BaseClient):
    """Asynchronous Client"""

    @decorators.authenticated
    async def get(self, path, *, on_response=None, on_error=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return await self.a_request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    async def put(self, path, data, *, data_serializer=None, on_response=None, on_error=None, **kwargs):
        request = async_requests.PutRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return await self.a_request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    async def post(self, path, data, *, data_serializer=None, on_response=None, on_error=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return await self.a_request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    async def form_data(self, path, data, *, on_response=None, on_error=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=Serializers.FormData(data), **kwargs)
        return await self.a_request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    async def delete(self, path, *, on_response=None, on_error=None, **kwargs):
        request = async_requests.DeleteRequest(self._builder(path), **kwargs)
        return await self.a_request(request, on_response=on_response, on_error=on_error)

    async def _request(self, request, *, on_response=None, on_error=None):
        on_response = on_response if on_response else AsyncResponse.new()
        response = await self._session.await_promise(self.join_headers(request), on_response=on_response)
        return response if response.ok else await on_error.a_accept(response)


class AsyncFolders(AsyncClient):

    async def download_zip(self, path, data, **kwargs):
        return await super().form_data(path, data, **kwargs)


class AsyncUpload(AsyncClient):

    async def upload(self, path, data, **kwargs):
        return await super().form_data(path, data, **kwargs)


class AsyncWebDAV(AsyncClient):
    """WebDAV"""

    async def download(self, path, **kwargs):
        return await super().get(path, on_error=XMLHandler(), **kwargs)

    @decorators.authenticated
    async def propfind(self, path, depth, **kwargs):
        request = async_requests.PropfindRequest(self._builder(path), headers={'depth': str(depth)}, **kwargs)
        response = await self.a_request(request, on_error=XMLHandler())
        return await response.dav()

    @decorators.authenticated
    async def mkcol(self, path, **kwargs):
        request = async_requests.MkcolRequest(self._builder(path), **kwargs)
        response = await self.a_request(request, on_error=XMLHandler())
        return await response.text()

    @decorators.authenticated
    async def copy(self, source, destination, *, overwrite=False, **kwargs):
        request = async_requests.CopyRequest(self._builder(source), headers=self._webdav_headers(destination, overwrite), **kwargs)
        response = await self.a_request(request, on_error=XMLHandler())
        return await response.xml()

    @decorators.authenticated
    async def move(self, source, destination, *, overwrite=False, **kwargs):
        request = async_requests.MoveRequest(self._builder(source), headers=self._webdav_headers(destination, overwrite), **kwargs)
        response = await self.a_request(request, on_error=XMLHandler())
        return await response.xml()

    async def delete(self, path, **kwargs):  # pylint: disable=arguments-differ
        response = await super().delete(path, on_error=XMLHandler(), **kwargs)
        return await response.text()

    def _webdav_headers(self, destination, overwrite):
        return {
            'Destination': self._builder(destination),
            'Overwrite': 'T' if overwrite is True else 'F'
        }


class AsyncJSON(AsyncClient):

    def __init__(self, builder=None, session=None, settings=None, authenticator=None):
        super().__init__(builder, session, settings, authenticator)
        self.headers.persist_headers({'Content-Type': 'application/json'})

    async def get(self, path, **kwargs):
        response = await super().get(path, on_error=JSONHandler(), **kwargs)
        return await response.json()

    async def put(self, path, data, **kwargs):
        response = await super().put(path, data, data_serializer=Serializers.JSON, on_error=JSONHandler(), **kwargs)
        return await response.json()

    async def post(self, path, data, **kwargs):
        response = await super().post(path, data, data_serializer=Serializers.JSON, on_error=JSONHandler(), **kwargs)
        return await response.json()

    async def delete(self, path, **kwargs):
        response = await super().delete(path, on_error=JSONHandler(), **kwargs)
        return await response.json()


class AsyncXML(AsyncClient):

    async def get(self, path, **kwargs):
        response = await super().get(path, on_error=XMLHandler(), **kwargs)
        return await response.xml()

    async def put(self, path, data, **kwargs):
        response = await super().put(path, data, data_serializer=Serializers.XML, on_error=XMLHandler(), **kwargs)
        return await response.xml()

    async def post(self, path, data, **kwargs):
        response = await super().post(path, data, data_serializer=Serializers.XML, on_error=XMLHandler(), **kwargs)
        return await response.xml()

    async def delete(self, path, **kwargs):
        response = await super().delete(path, on_error=XMLHandler(), **kwargs)
        return await response.xml()


class AsyncExtended(AsyncXML):
    """CTERA Schema"""

    async def get_multi(self, path, paths, **kwargs):
        return await self.database(path, 'get-multi', paths, **kwargs)

    async def execute(self, path, name, param=None, **kwargs):  # schema method
        return await self._execute(path, 'user-defined', name, param, **kwargs)

    async def database(self, path, name, param=None, **kwargs):  # schema method
        return await self._execute(path, 'db', name, param, **kwargs)

    async def _execute(self, path, _type, name, param, **kwargs):
        data = Object()
        data.type = _type
        data.name = name
        data.param = param
        return await super().post(path, data, **kwargs)


class AsyncAPI(AsyncExtended):
    """CTERA Management API"""

    async def web_session(self):
        response = await AsyncClient.get(self, '/currentSession')
        self.headers.persist_response_header(response, 'X-CTERA-TOKEN')
        return await response.xml()

    async def defaults(self, classname):
        return self.get(f'/defaults/{classname}')


class AsyncResponse(BaseResponse):
    """Asynchronous Response Object"""

    async def a_iter_content(self, chunk_size=None):
        async for chunk in self._response.content.iter_chunked(chunk_size if chunk_size else 5120):
            yield chunk

    async def text(self):
        return await self._response.text()

    async def json(self):
        return Deserializers.JSON(await self._response.read())

    async def xml(self):
        return Deserializers.XML(await self._response.read())

    async def dav(self):
        return Deserializers.DAV(await self._response.read())

    @async_requests.decorate_stream_error
    async def read(self, n=-1):
        return await self._response.content.read(n)

    @staticmethod
    def new():
        async def new_response(response):
            return AsyncResponse(response)
        return new_response


class Client(BaseClient):
    """Synchronous Client"""

    @decorators.authenticated
    def handle(self, path, *, on_response=None, on_error=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return self.request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    def get(self, path, *, on_response=None, on_error=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return self.request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    def put(self, path, data, *, data_serializer=None, on_response=None, on_error=None, **kwargs):
        request = async_requests.PutRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return self.request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    def post(self, path, data, *, data_serializer=None, on_response=None, on_error=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return self.request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    def form_data(self, path, data, *, on_response=None, on_error=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=Serializers.FormData(data), **kwargs)
        return self.request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    def multipart(self, path, form, *, on_response=None, on_error=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=form.data, **kwargs)
        return self.request(request, on_response=on_response, on_error=on_error)

    @decorators.authenticated
    def delete(self, path, *, on_response=None, on_error=None, **kwargs):
        request = async_requests.DeleteRequest(self._builder(path), **kwargs)
        return self.request(request, on_response=on_response, on_error=on_error)

    def _request(self, request, *, on_response=None, on_error=None):
        on_response = on_response if on_response else SyncResponse.new()
        response = execute(self._session.await_promise, self.join_headers(request), on_response=on_response)
        return response if response.ok else on_error.accept(response)

    def close(self):  # pylint: disable=invalid-overridden-method
        return execute(super().close)


class Folders(Client):

    def download_zip(self, path, data, **kwargs):
        return super().form_data(path, data, **kwargs)


class Upload(Client):

    def upload(self, path, data, **kwargs):
        return super().form_data(path, data, **kwargs)


class WebDAV(Client):

    def download(self, path, **kwargs):
        return super().handle(path, on_error=XMLHandler(), **kwargs)

    @decorators.authenticated
    def propfind(self, path, depth, **kwargs):
        request = async_requests.PropfindRequest(self._builder(path), headers={'depth': str(depth)}, **kwargs)
        response = self.request(request, on_error=XMLHandler())
        return response.dav()

    @decorators.authenticated
    def mkcol(self, path, **kwargs):
        request = async_requests.MkcolRequest(self._builder(path), **kwargs)
        response = self.request(request, on_error=XMLHandler())
        return response.text()

    @decorators.authenticated
    def copy(self, source, destination, *, overwrite=False, **kwargs):
        request = async_requests.CopyRequest(self._builder(source), headers=self._webdav_headers(destination, overwrite), **kwargs)
        response = self.request(request, on_error=XMLHandler())
        return response.xml()

    @decorators.authenticated
    def move(self, source, destination, *, overwrite=False, **kwargs):
        request = async_requests.MoveRequest(self._builder(source), headers=self._webdav_headers(destination, overwrite), **kwargs)
        response = self.request(request, on_error=XMLHandler())
        return response.xml()

    def delete(self, path, **kwargs):  # pylint: disable=arguments-differ
        response = super().delete(path, on_error=XMLHandler(), **kwargs)
        return response.text()

    def _webdav_headers(self, destination, overwrite):
        return {
            'Destination': self._builder(destination),
            'Overwrite': 'T' if overwrite is True else 'F'
        }


class XML(Client):
    """XML Serializer and Deserializer"""

    def __init__(self, builder=None, session=None, settings=None, authenticator=None):
        super().__init__(builder, session, settings, authenticator)
        self._type = {'Content-Type': 'text/plain'}

    def get(self, path, **kwargs):
        response = super().get(path, on_error=XMLHandler(), **kwargs)
        return response.xml()

    def put(self, path, data, **kwargs):
        response = super().put(path, data, data_serializer=Serializers.XML, headers=self._type, on_error=XMLHandler(), **kwargs)
        return response.xml()

    def post(self, path, data, **kwargs):
        response = super().post(path, data, data_serializer=Serializers.XML, headers=self._type, on_error=XMLHandler(), **kwargs)
        return response.xml()

    def form_data(self, path, data, **kwargs):
        response = super().form_data(path, data, on_error=XMLHandler(), **kwargs)
        return response.xml()

    def delete(self, path, **kwargs):
        response = super().delete(path, on_error=XMLHandler(), **kwargs)
        return response.xml()


class JSON(Client):
    """JSON Serializer and Deserializer"""

    def get(self, path, **kwargs):
        response = super().get(path, on_error=JSONHandler(), **kwargs)
        return response.json()

    def put(self, path, data, **kwargs):
        response = super().put(path, data, data_serializer=Serializers.JSON, on_error=JSONHandler(), **kwargs)
        return response.json()

    def post(self, path, data, **kwargs):
        response = super().post(path, data, data_serializer=Serializers.JSON, on_error=JSONHandler(), **kwargs)
        return response.json()

    def delete(self, path, **kwargs):
        response = super().delete(path, on_error=JSONHandler(), **kwargs)
        return response.json()


class Extended(XML):
    """CTERA Schema"""

    def get_multi(self, path, paths, **kwargs):
        return self.database(path, 'get-multi', paths, **kwargs)

    def show_multi(self, path, paths, **kwargs):
        print(Serializers.JSON(self.get_multi(path, paths, **kwargs), no_log=False))

    def execute(self, path, name, param=None, **kwargs):  # schema method
        return self._execute(path, 'user-defined', name, param, **kwargs)

    def database(self, path, name, param=None, **kwargs):  # schema method
        return self._execute(path, 'db', name, param, **kwargs)

    def add(self, path, param=None, **kwargs):
        return self.database(path, 'add', param, **kwargs)

    def _execute(self, path, _type, name, param, **kwargs):
        data = Object()
        data.type = _type
        data.name = name
        data.param = param
        return super().post(path, data, **kwargs)


class API(Extended):
    """CTERA Management API"""

    def web_session(self):
        response = Client.get(self, '/currentSession')
        self.headers.persist_response_header(response, 'X-CTERA-TOKEN')
        return response.xml()

    def defaults(self, classname):
        return self.get(f'/defaults/{classname}')


class Migrate(JSON):
    """CTERA Migrate Service"""

    def login(self):
        response = Client.get(self, '/auth/user', on_error=JSONHandler())
        self.headers.persist_response_header(response, 'x-mt-x')
        return response.json()


event_loop = asyncio.new_event_loop()


def execute(target, *args, **kwargs):
    loop = asyncio.get_event_loop()

    if not loop.is_running():
        return loop.run_until_complete(target(*args, **kwargs))

    return run_threadsafe(event_loop, target, *args, **kwargs)


class SyncResponse(AsyncResponse):
    """Synchronous Response Object"""

    def iter_content(self, chunk_size=None):
        while True:
            try:
                yield execute(super().a_iter_content(chunk_size).__anext__)
            except StopAsyncIteration:
                break

    def text(self):  # pylint: disable=invalid-overridden-method
        return execute(super().text)

    def json(self):  # pylint: disable=invalid-overridden-method
        return execute(super().json)

    def xml(self):  # pylint: disable=invalid-overridden-method
        return execute(super().xml)

    def dav(self):  # pylint: disable=invalid-overridden-method
        return execute(super().dav)

    @staticmethod
    def new():
        async def new_response(response):
            return SyncResponse(response)
        return new_response
