from .http import HTTPClient, ContentType, HTTPException, HTTPResponse, geturi
from ..convert import fromxmlstr, toxmlstr
from ..exception import CTERAClientException
from ..lib import Command
from ..common import Object
from ..transcript import transcribe
from .. import config

class CTERAClient(HTTPClient):

    def get(self, baseurl, path, params=None):
        function = Command(HTTPClient.get, self, geturi(baseurl, path), params if params else {})
        return self._execute(function, CTERAClient.fromxmlstr)

    def download(self, baseurl, path, params):
        function = Command(HTTPClient.get, self, geturi(baseurl, path), params)
        return self._execute(function, CTERAClient.file_descriptor)

    def get_multi(self, baseurl, path, paths):
        return self.db(baseurl, path, "get-multi", paths)

    def put(self, baseurl, path, data):
        function = Command(HTTPClient.put, self, geturi(baseurl, path), ContentType.textplain, toxmlstr(data))
        return self._execute(function, CTERAClient.fromxmlstr)

    def post(self, baseurl, path, data):
        function = Command(HTTPClient.post, self, geturi(baseurl, path), ContentType.textplain, toxmlstr(data))
        return self._execute(function, CTERAClient.fromxmlstr)

    def form_data(self, baseurl, path, form_data):
        function = Command(HTTPClient.post, self, geturi(baseurl, path), ContentType.urlencoded, form_data, True)
        return self._execute(function, CTERAClient.fromxmlstr)

    def execute(self, baseurl, path, name, param=None):
        return self._ctera_exec(baseurl, path, 'user-defined', name, param)

    def delete(self, baseurl, path):
        function = Command(HTTPClient.delete, self, geturi(baseurl, path))
        return self._execute(function, CTERAClient.fromxmlstr)

    def mkcol(self, baseurl, path):
        function = Command(HTTPClient.mkcol, self, geturi(baseurl, path))
        return self._execute(function, CTERAClient.fromxmlstr)

    def db(self, baseurl, path, name, param):
        return self._ctera_exec(baseurl, path, 'db', name, param)

    def _ctera_exec(self, baseurl, path, exec_type, name, param):
        obj = Object()
        obj.type = exec_type
        obj.name = name
        obj.param = param
        function = Command(HTTPClient.post, self, geturi(baseurl, path), ContentType.textplain, toxmlstr(obj))
        return self._execute(function, CTERAClient.fromxmlstr)

    @staticmethod
    def fromxmlstr(request, response):
        if not config.transcript['disabled']:
            response = HTTPResponse(response)
            transcribe.transcribe(request, response)
        return fromxmlstr(response.read())

    @staticmethod
    def file_descriptor(request, response):
        if not config.transcript['disabled']:
            transcribe.transcribe(request)
        return response

    @staticmethod
    def _execute(function, return_function):
        try:
            request, response = function()
            return return_function(request, response)
        except HTTPException as http_error:
            client_error = CTERAClientException()
            client_error.__dict__ = http_error.__dict__.copy()
            raise client_error
