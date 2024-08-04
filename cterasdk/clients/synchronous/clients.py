
import time
import asyncio
import logging
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
        return execute_request(self._async_session, self.join_headers(request), on_response=on_response)

    def close(self):  # pylint: disable=invalid-overridden-method
        return asyncio.get_event_loop().run_until_complete(super().close())


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

    def get(self, path, **kwargs):
        response = super().get(path, **kwargs)
        return response.xml()

    def put(self, path, data, **kwargs):
        response = super().put(path, data, data_serializer=Serializers.XML, **kwargs)
        return response.xml()

    def post(self, path, data, **kwargs):
        response = super().post(path, data, data_serializer=Serializers.XML, **kwargs)
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


def execute_request(async_session, request, *, on_response, max_retries=3, backoff_factor=2):
    retries = 0
    while retries < max_retries:
        try:
            response = asyncio.get_event_loop().run_until_complete(async_session.await_promise(request, on_response=on_response))
            return errors.accept(response)
        except (ConnectionError, TimeoutError):
            retries += 1
            if retries < max_retries:
                delay = backoff_factor ** retries
                logging.getLogger('cterasdk.http').warning("Retrying in %s seconds.", delay)
                time.sleep(delay)
            else:
                logging.getLogger('cterasdk.http').error("Max retries reached. Request failed.")
                raise
    return None


class SyncResponse(AsyncResponse):
    """Synchronous Response Object"""

    def __init__(self, response):
        super().__init__(response)
        self._executor = asyncio.get_event_loop()

    def iter_content(self, chunk_size=None):
        while True:
            try:
                yield self._executor.run_until_complete(super().async_iter_content(chunk_size).__anext__())
            except StopAsyncIteration:
                break

    def text(self):  # pylint: disable=invalid-overridden-method
        return self._consume_response(super().text)

    def json(self):  # pylint: disable=invalid-overridden-method
        return self._consume_response(super().json)

    def xml(self):  # pylint: disable=invalid-overridden-method
        return self._consume_response(super().xml)

    def _consume_response(self, consumer):
        return self._executor.run_until_complete(consumer())

    @staticmethod
    def new():
        async def new_response(response):
            return SyncResponse(response)
        return new_response
