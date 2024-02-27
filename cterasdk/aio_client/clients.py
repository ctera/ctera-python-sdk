
import time
import asyncio
import logging
import cterasdk.settings
from . import async_requests, errors, decorators
from .async_responses import Response, Deserializers
from ..convert import tojsonstr, toxmlstr
from ..common import Object, utils


class Serializers:
    JSON = tojsonstr
    XML = toxmlstr
    FormData = async_requests.FormData


class CookieJar:

    def __init__(self, cookies, response_url):
        self._cookies = cookies
        self._response_url = response_url

    @property
    def all(self):
        return {v.key: v.value for v in self._cookies.filter_cookies(self._response_url).values()}

    def update(self, cookies):
        self._cookies.update_cookies(cookies, self._response_url)


class PersistentHeaders:
    """Headers to include in every request"""

    def __init__(self):
        self._headers = {}

    @property
    def all(self):
        return self._headers

    def update_headers(self, headers):
        self._headers.update(headers)


class MultipartForm:
    """Multipart Request Form"""

    def __init__(self):
        self._data = async_requests.FormData()

    def add(self, name, value, filename=None, content_transfer_encoding=None):
        self._data.add_field(name=name, value=value, filename=filename,
                             content_type='multipart/form-data', content_transfer_encoding=content_transfer_encoding)

    @property
    def data(self):
        return self._data


class Client:
    """Synchronous Client"""

    def __init__(self, builder=None, async_session=None, authenticator=None):
        """
        Initialize a Synchronous Client

        :param builder: Endpoint builder.
        :param ,optional async_session: Re-use an asynchronous session.
        :param ,optional authenticator: Authenticator function.
        """
        self._headers = PersistentHeaders()
        self._authenticator = authenticator
        self._builder = builder
        self._async_session = async_session if async_session else async_requests.Session(**session_settings())

    @decorators.authenticated
    def handle(self, path, *, on_response=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return self._request(request, on_response=on_response)

    @decorators.authenticated
    def get(self, path, *, on_response=None, **kwargs):
        request = async_requests.GetRequest(self._builder(path), **kwargs)
        return self._request(request, on_response=on_response)

    @decorators.authenticated
    def put(self, path, data, *, data_serializer=None, on_response=None, **kwargs):
        request = async_requests.PutRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return self._request(request, on_response=on_response)

    @decorators.authenticated
    def post(self, path, data, *, data_serializer=None, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=data_serializer(data), **kwargs)
        return self._request(request, on_response=on_response)

    @decorators.authenticated
    def form_data(self, path, data, *, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=Serializers.FormData(data), **kwargs)
        return self._request(request, on_response=on_response)

    @decorators.authenticated
    def multipart(self, path, form, *, on_response=None, **kwargs):
        request = async_requests.PostRequest(self._builder(path), data=form.data, **kwargs)
        return self._request(request, on_response=on_response)

    @decorators.authenticated
    def delete(self, path, *, on_response=None, **kwargs):
        request = async_requests.DeleteRequest(self._builder(path), **kwargs)
        return self._request(request, on_response=on_response)

    def _request(self, request, *, on_response):
        request.kwargs['headers'] = utils.merge(request.kwargs.get('headers', None), self.headers.all)
        on_response = on_response if on_response else Response.new()
        return execute_request(self._async_session, request, on_response=on_response)

    @property
    def cookies(self):
        return CookieJar(self._async_session.cookies, self._builder())

    @property
    def headers(self):
        return self._headers

    @property
    def baseurl(self):
        return self._builder()

    def shutdown(self):
        return asyncio.get_event_loop().run_until_complete(self._async_session.shutdown())

    def __str__(self):
        return f"({self.__class__.__name__} client at {hex(hash(self))}, baseurl={self._builder()})"


class Folders(Client):

    def download_zip(self, path, data, **kwargs):
        return super().form_data(path, data, on_response=Response.new(), **kwargs)


class Upload(Client):

    def upload(self, path, data, **kwargs):
        return super().form_data(path, data, on_response=Response.new(), **kwargs)


class Dav(Client):
    """WebDAV"""

    def download(self, path, **kwargs):
        return super().handle(path, **kwargs)

    def mkcol(self, path):
        request = async_requests.MkcolRequest(self._builder(path))
        response = self._request(request, on_response=Response.new())
        return response.text

    def copy(self, source, destination, *, overwrite=False):
        request = async_requests.CopyRequest(self._builder(source), headers=self._webdav_headers(destination, overwrite))
        response = self._request(request, on_response=Response.new(Deserializers.XML))
        return response.deserialize()

    def move(self, source, destination, *, overwrite=False):
        request = async_requests.MoveRequest(self._builder(source), headers=self._webdav_headers(destination, overwrite))
        response = self._request(request, on_response=Response.new(Deserializers.XML))
        return response.deserialize()

    def delete(self, path):  # pylint: disable=arguments-differ
        response = super().delete(path, on_response=Response.new())
        return response.text

    def _webdav_headers(self, destination, overwrite):
        return {
            'Destination': self._builder(destination),
            'Overwrite': 'T' if overwrite is True else 'F'
        }


class XML(Client):
    """XML Serializer and Deserializer"""

    def get(self, path, **kwargs):
        response = super().get(path, on_response=Response.new(Deserializers.XML), **kwargs)
        return response.deserialize()

    def put(self, path, data, **kwargs):
        response = super().put(path, data, data_serializer=Serializers.XML, on_response=Response.new(Deserializers.XML), **kwargs)
        return response.deserialize()

    def post(self, path, data, **kwargs):
        response = super().post(path, data, data_serializer=Serializers.XML, on_response=Response.new(Deserializers.XML), **kwargs)
        return response.deserialize()

    def form_data(self, path, data, **kwargs):
        response = super().form_data(path, data, on_response=Response.new(Deserializers.XML), **kwargs)
        return response.deserialize()

    def delete(self, path, **kwargs):
        response = super().delete(path, on_response=Response.new(Deserializers.XML), **kwargs)
        return response.deserialize()


class JSON(Client):
    """JSON Serializer and Deserializer"""

    def get(self, path, **kwargs):
        response = super().get(path, on_response=Response.new(Deserializers.JSON), **kwargs)
        return response.deserialize()

    def put(self, path, data, **kwargs):
        response = super().put(path, data, data_serializer=Serializers.JSON, on_response=Response.new(Deserializers.JSON), **kwargs)
        return response.deserialize()

    def post(self, path, data, **kwargs):
        response = super().post(path, data, data_serializer=Serializers.JSON, on_response=Response.new(Deserializers.JSON), **kwargs)
        return response.deserialize()

    def delete(self, path, **kwargs):
        response = super().delete(path, on_response=Response.new(Deserializers.JSON), **kwargs)
        return response.deserialize()

    def _request(self, request, *, on_response=None):
        return super()._request(request, on_response=on_response)


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
        response = self._request(request, on_response=Response.new(Deserializers.JSON))
        token = response.headers.get(Migrate.ID, None)
        if token:
            self.headers.update_headers({Migrate.ID: token})
        return response.deserialize()


def execute_request(async_session, request, *, on_response, max_retries=3, backoff_factor=2):
    retries = 0
    while retries < max_retries:
        try:
            response = asyncio.get_event_loop().run_until_complete(async_session.await_promise(request, on_response=on_response))
            return errors.accept_response(response)
        except (ConnectionError, TimeoutError):
            retries += 1
            if retries < max_retries:
                delay = backoff_factor ** retries
                logging.getLogger().warning("Retrying in %s seconds.", delay)
                time.sleep(delay)
            else:
                logging.getLogger().error("Max retries reached. Request failed.")
                raise
    return None


def session_settings():
    return {
        'connector': async_requests.create_connector(ssl=cterasdk.settings.sessions.management.ssl),
        'cookie_jar': async_requests.create_cookie_jar(unsafe=cterasdk.settings.sessions.management.allow_unsafe)
    }
