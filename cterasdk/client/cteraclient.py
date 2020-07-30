from .http import HTTPClient, ContentType, HTTPException, HTTPResponse, geturi
from ..convert import fromxmlstr, toxmlstr
from ..exception import CTERAClientException
from ..lib import Command
from ..common import Object
from ..transcript import transcribe
from .. import config


class CTERAClient:

    def __init__(self, session_id_key):
        self.http_client = HTTPClient(session_id_key)

    def get(self, baseurl, path, params=None):
        function = Command(HTTPClient.get, self.http_client, geturi(baseurl, path), params if params else {})
        return self._execute(function)

    def download(self, baseurl, path, params):
        function = Command(HTTPClient.get, self.http_client, geturi(baseurl, path), params, None, True)
        return self._execute(function, return_function=CTERAClient.file_descriptor)

    def download_zip(self, baseurl, path, form_data):
        function = Command(HTTPClient.post, self.http_client, geturi(baseurl, path), ContentType.urlencoded, form_data, True)
        return self._execute(function, return_function=CTERAClient.file_descriptor)

    def get_multi(self, baseurl, path, paths):
        return self.db(baseurl, path, "get-multi", paths)

    def put(self, baseurl, path, data):
        function = Command(HTTPClient.put, self.http_client, geturi(baseurl, path), ContentType.textplain, toxmlstr(data))
        return self._execute(function)

    def post(self, baseurl, path, data):
        function = Command(HTTPClient.post, self.http_client, geturi(baseurl, path), ContentType.textplain, toxmlstr(data))
        return self._execute(function)

    def form_data(self, baseurl, path, form_data):
        function = Command(HTTPClient.post, self.http_client, geturi(baseurl, path), ContentType.urlencoded, form_data, True)
        return self._execute(function)

    def execute(self, baseurl, path, name, param=None):
        return self._ctera_exec(baseurl, path, 'user-defined', name, param)

    def delete(self, baseurl, path):
        function = Command(HTTPClient.delete, self.http_client, geturi(baseurl, path))
        return self._execute(function)

    def mkcol(self, baseurl, path):
        function = Command(HTTPClient.mkcol, self.http_client, geturi(baseurl, path))
        return self._execute(function)

    def db(self, baseurl, path, name, param):
        return self._ctera_exec(baseurl, path, 'db', name, param)

    def multipart(self, baseurl, path, form_data):
        function = Command(HTTPClient.multipart, self.http_client, geturi(baseurl, path), form_data)
        return self._execute(function)

    def upload(self, baseurl, path, form_data):
        function = Command(HTTPClient.upload, self.http_client, geturi(baseurl, path), form_data)
        return self._execute(function)

    def _ctera_exec(self, baseurl, path, exec_type, name, param):
        obj = Object()
        obj.type = exec_type
        obj.name = name
        obj.param = param
        function = Command(HTTPClient.post, self.http_client, geturi(baseurl, path), ContentType.textplain, toxmlstr(obj))
        return self._execute(function)

    def get_session_id(self):
        return self.http_client.get_session_id()

    def set_session_id(self, session_id):
        return self.http_client.set_session_id(session_id)

    @staticmethod
    def fromxmlstr(request, response):
        if not config.transcript['disabled']:
            response = HTTPResponse(response)
            transcribe.transcribe(request, response)
        return fromxmlstr(response.text)

    @staticmethod
    def file_descriptor(request, response):
        if not config.transcript['disabled']:
            transcribe.transcribe(request)
        return response

    @staticmethod
    def _execute(function, return_function=None):
        return_function = return_function or CTERAClient.fromxmlstr
        try:
            request, response = function()
            return return_function(request, response)
        except HTTPException as http_error:
            client_error = CTERAClientException()
            client_error.__dict__ = http_error.__dict__.copy()
            raise client_error
