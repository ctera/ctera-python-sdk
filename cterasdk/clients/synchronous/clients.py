
import asyncio
import threading
from . import errors
from ..base import BaseClient
from ..common import Serializers
from ..asynchronous.clients import AsyncResponse
from ...common import Object
from .. import async_requests, decorators


class Client(BaseClient):
    """Synchronous Client"""

    @decorators.authenticated
    def handle(self, path, *, on_response=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return self.request(request, on_response=on_response)

    @decorators.authenticated
    def get(self, path, *, on_response=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return self.request(request, on_response=on_response)

    @decorators.authenticated
    def put(self, path, data, *, data_serializer=None, on_response=None, **kwargs):
        request = async_requests.PutRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return self.request(request, on_response=on_response)

    @decorators.authenticated
    def post(self, path, data, *, data_serializer=None, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return self.request(request, on_response=on_response)

    @decorators.authenticated
    def form_data(self, path, data, *, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=Serializers.FormData(data), **kwargs)
        return self.request(request, on_response=on_response)

    @decorators.authenticated
    def multipart(self, path, form, *, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=form.data, **kwargs)
        return self.request(request, on_response=on_response)

    @decorators.authenticated
    def delete(self, path, *, on_response=None, **kwargs):
        request = async_requests.DeleteRequest(self._builder(path), **kwargs)
        return self.request(request, on_response=on_response)

    def _request(self, request, *, on_response=None):
        on_response = on_response if on_response else SyncResponse.new()
        response = execute(self._session.await_promise, self.join_headers(request), on_response=on_response)
        return errors.accept(response)

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
        return super().handle(path, **kwargs)

    def mkcol(self, path):
        request = async_requests.MkcolRequest(self._builder(path))
        response = self.request(request)
        return response.text()

    def copy(self, source, destination, *, overwrite=False):
        request = async_requests.CopyRequest(self._builder(source), headers=self._webdav_headers(destination, overwrite))
        response = self.request(request)
        return response.xml()

    def move(self, source, destination, *, overwrite=False):
        request = async_requests.MoveRequest(self._builder(source), headers=self._webdav_headers(destination, overwrite))
        response = self.request(request)
        return response.xml()

    def delete(self, path):  # pylint: disable=arguments-differ
        response = super().delete(path)
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
        response = super().get(path, **kwargs)
        return response.xml()

    def put(self, path, data, **kwargs):
        response = super().put(path, data, data_serializer=Serializers.XML, headers=self._type, **kwargs)
        return response.xml()

    def post(self, path, data, **kwargs):
        response = super().post(path, data, data_serializer=Serializers.XML, headers=self._type, **kwargs)
        return response.xml()

    def form_data(self, path, data, **kwargs):
        response = super().form_data(path, data, **kwargs)
        return response.xml()

    def delete(self, path, **kwargs):
        response = super().delete(path, **kwargs)
        return response.xml()


class JSON(Client):
    """JSON Serializer and Deserializer"""

    def get(self, path, **kwargs):
        response = super().get(path, **kwargs)
        return response.json()

    def put(self, path, data, **kwargs):
        response = super().put(path, data, data_serializer=Serializers.JSON, **kwargs)
        return response.json()

    def post(self, path, data, **kwargs):
        response = super().post(path, data, data_serializer=Serializers.JSON, **kwargs)
        return response.json()

    def delete(self, path, **kwargs):
        response = super().delete(path, **kwargs)
        return response.json()


class Extended(XML):
    """CTERA Schema"""

    def get_multi(self, path, paths):
        return self.database(path, 'get-multi', paths)

    def show_multi(self, path, paths):
        print(Serializers.JSON(self.get_multi(path, paths), no_log=False))

    def execute(self, path, name, param=None):  # schema method
        return self._execute(path, 'user-defined', name, param)

    def database(self, path, name, param=None):  # schema method
        return self._execute(path, 'db', name, param)

    def add(self, path, param=None):
        return self.database(path, 'add', param)

    def _execute(self, path, _type, name, param):
        data = Object()
        data.type = _type
        data.name = name
        data.param = param
        return super().post(path, data)


class API(Extended):
    """CTERA Management API"""

    def defaults(self, classname):
        return self.get(f'/defaults/{classname}')


class Migrate(JSON):
    """CTERA Migrate Service"""

    ID = 'x-mt-x'

    def login(self):
        request = async_requests.GetRequest(self._builder('/auth/user'))
        response = self.request(request)
        token = response.headers.get(Migrate.ID, None)
        if token:
            self.headers.update_headers({Migrate.ID: token})
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
                yield execute(super().async_iter_content(chunk_size).__anext__)
            except StopAsyncIteration:
                break

    def text(self):  # pylint: disable=invalid-overridden-method
        return execute(super().text)

    def json(self):  # pylint: disable=invalid-overridden-method
        return execute(super().json)

    def xml(self):  # pylint: disable=invalid-overridden-method
        return execute(super().xml)

    @staticmethod
    def new():
        async def new_response(response):
            return SyncResponse(response)
        return new_response


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
