from .http import HTTPClient, ContentType, HTTPException, HTTPResponse, geturi

from ..convert import fromxmlstr, toxmlstr

from ..exception import CTERAException

from ..exception import CTERAClientException

from ..lib import Command

from ..common import Object

from ..transcript import transcribe

from .. import config

import copy

import re

class CTERAClient(HTTPClient):
    
    def __init__(self):
        
        HTTPClient.__init__(self)
      
    def get(self, baseurl, path, params = {}):
        
        function = Command(HTTPClient.get, self, geturi(baseurl, path), params)
        
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
        
    def execute(self, baseurl, path, name, param = None):
        
        return self.ctera_exec(baseurl, path, 'user-defined', name, param)
    
    def delete(self, baseurl, path):
        
        function = Command(HTTPClient.delete, self, geturi(baseurl, path))
        
        return self._execute(function, CTERAClient.fromxmlstr)
    
    def mkcol(self, baseurl, path):
        
        function = Command(HTTPClient.mkcol, self, geturi(baseurl, path))
        
        return self._execute(function, CTERAClient.fromxmlstr)
    
    def db(self, baseurl, path, name, param):
        
        return self.ctera_exec(baseurl, path, 'db', name, param)
    
    def ctera_exec(self, baseurl, path, type, name, param):
        
        obj = Object()
        
        obj.type = type
        
        obj.name = name
        
        obj.param = param
        
        function = Command(HTTPClient.post, self, geturi(baseurl, path), ContentType.textplain, toxmlstr(obj))
        
        return self._execute(function, CTERAClient.fromxmlstr)
    
    def fromxmlstr(request, response):
        
        if not config.transcript['disabled']:
            
            response = HTTPResponse(response)
            
            transcribe.transcribe(request, response)
            
        return fromxmlstr(response.read())
    
    def file_descriptor(request, response):
        
        if not config.transcript['disabled']:
        
            transcribe.transcribe(request)
        
        return response
        
    def _execute(self, function, return_function):
        
        try:
            
            request, response = function()
            
            return return_function(request, response)
            
        except HTTPException as http_error:
            
            client_error = CTERAClientException()
            
            client_error.__dict__ = http_error.__dict__.copy()
            
            raise client_error
            