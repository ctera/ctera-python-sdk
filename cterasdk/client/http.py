from urllib.request import Request, BaseHandler, HTTPCookieProcessor, HTTPSHandler, build_opener

import urllib.parse

from urllib.error import HTTPError, URLError

from http.cookiejar import CookieJar

from .ssl import CertificateServices

from ..convert import fromxmlstr

from ..common import Object

from .. import config

from ..exception import SSLException, HostUnreachable, ExhaustedException

from ..lib import Version

from ..lib import ask

from abc import ABC, abstractmethod

from ssl import SSLError

import logging

import socket

class HTTPException(Exception):

    def __init__(self, req, code, hdrs, msg, fp):

        self.response = Object()
        
        self.response.code   = code
        
        self.response.reason = msg.upper()
        
        response = fp.read()
        
        try:
        
            self.response.body = fromxmlstr(response)
            
        except Exception as error:
            
            pass
        
        if config.http['verbose']:
            
            self.response.headers = hdrs
        
            self.request  = parse_request(req)

class CTERAClientHandler(BaseHandler):

    def http_error_400(self, req, fp, code, msg, hdrs):
        
        raise HTTPException(req, code, hdrs, msg, fp)
        
    def http_error_401(self, req, fp, code, msg, hdrs):
        
        raise HTTPException(req, code, hdrs, msg, fp)
    
    def http_error_403(self, req, fp, code, msg, hdrs):
        
        raise HTTPException(req, code, hdrs, msg, fp)
        
    def http_error_404(self, req, fp, code, msg, hdrs):
        
        raise HTTPException(req, code, hdrs, msg, fp)
        
    def http_error_405(self, req, fp, code, msg, hdrs):
        
        raise HTTPException(req, code, hdrs, msg, fp)
    
    def http_error_500(self, req, fp, code, msg, hdrs):
        
        raise HTTPException(req, code, hdrs, msg, fp)
        
class SessionHandler(HTTPCookieProcessor):
    
    def __init__(self):
        
        self.cj = CookieJar()
        
        HTTPCookieProcessor.__init__(self, self.cj)
        
class TLSHandler(HTTPSHandler):
    
    def __init__(self, hostport = None):
        
        context = None
        
        if hostport != None:
            
            host, port = hostport
        
            context = CertificateServices.add_trusted_cert(host, port)
        
        HTTPSHandler.__init__(self, context = context)

class HTTPResponse:
    
    def __init__(self, response):
        
        self.url = response.geturl()
        
        self.code = response.getcode()
        
        self.headers = response.headers
        
        self.data = response.read()
        
    def geturl(self):
        
        return self.url
    
    def getcode(self):
        
        return self.code
        
    def read(self):
        
        return self.data
    
def parse_host(request):
    
    o = urllib.parse.urlparse(request.full_url)
    
    return o.hostname, o.port

def parse_request(request):

    o = urllib.parse.urlparse(request.full_url)
    
    target = Object()
    
    target.host = Object()
    
    target.host.scheme      = o.scheme
    
    target.host.hostname    = o.hostname
    
    target.host.port        = o.port
    
    target.method           = request.get_method()
    
    target.uri              = request.get_full_url()
    
    target.headers          = request.header_items()
    
    if request.data != None:
    
        target.body             = request.data.decode('utf-8')              # decode from 'Bytes' to 'UTF-8'
    
    return target

def geturi(baseurl, path):
    
    path = urllib.parse.quote(path)
    
    count = int(baseurl.endswith('/')) + int(path.startswith('/'))
    
    if count == 2:
        
        return baseurl[:-1] + path
    
    elif count == 1:
        
        return baseurl + path
    
    elif count == 0:
        
        return baseurl + '/' + path

class GetRequest(Request):
    
    def get_method(self):
        
        return 'GET'
    
class PutRequest(Request):
    
    def get_method(self):
        
        return 'PUT'
    
class PostRequest(Request):
    
    def get_method(self):
        
        return 'POST'
    
class DeleteRequest(Request):
    
    def get_method(self):
        
        return 'DELETE'
    
class MkColRequest(Request):
    
    def get_method(self):
        
        return 'MKCOL'
    
class ContentType:
    
    urlencoded = { 'Content-Type' : 'application/x-www-form-urlencoded' }
    
    textplain = { 'Content-Type' : 'text/plain' }

class AbstractHTTPClient(ABC):

    def __init__(self):
    
        super().__init__()
        
        self.timeout            = config.http['timeout']
        
        self.retries            = config.http['retries']
        
        self.ssl_error          = config.http['ssl']
        
        self.error_handler      = CTERAClientHandler
        
        self.session_handler    = SessionHandler()
        
        self.tls_handler        = TLSHandler()
        
        self.initialize_httpclient()
        
    def initialize_httpclient(self):
        
        self.httpclient            = build_opener(self.error_handler, self.session_handler, self.tls_handler)
        
        self.httpclient.addheaders = [('User-Agent', Version.instance().as_header())]
        
    @abstractmethod
    def dispatch_request(self, request):
        
        pass
        
    def _dispatch(self, request):
        
        response = self.dispatch_request(request)
        
        return (request, response)
            
    def dispatch(self, request):
        
        self.attempt = 0
        
        while self.attempt < self.retries:
            
            try:
                
                return self._dispatch(request)
            
            except HTTPError as error:
                
                raise HTTPException(request, error.code, error.hdrs, error.msg, error.fp)
            
            except socket.timeout as error:
                
                self.on_timeout()
                
            except URLError as error:
                
                if isinstance(error.reason, socket.gaierror):
                    
                    self.on_unreachable(request, error)
                    
                elif isinstance(error.reason, SSLError):
                    
                    self.on_ssl_error(request)
                    
                    self.reset()
                    
                else:
                
                    logging.getLogger().warn(error.reason)
            
            self.increment()
            
        logging.getLogger().error('Reached maximum number of retries. {0}'.format({'retries' : self.retries, 'timeout' : self.timeout}))
        
        raise ExhaustedException(self.retries, self.timeout)
        
    def on_unreachable(self, request, error):
        
        target = parse_request(request)
        
        scheme, host, port = target.host.scheme, target.host.hostname, target.host.port
        
        logging.getLogger().error('Cannot reach target host. {0}'.format({'host' : host, 'port' : port}))
        
        socket = Object()
        
        socket.errno    = error.reason.errno
        
        socket.message  = error.reason.strerror
        
        raise HostUnreachable(socket, host, port, scheme.upper())
                    
    def on_timeout(self):
        
        logging.getLogger().warn('Request timed out. {0}'.format({'attempt' : (self.attempt + 1)}))
        
    def on_ssl_error(self, request):
        
        host, port = parse_host(request)
        
        if self.should_trust(host, port):

            self.trust(host, port)
            
        else:
            
            raise SSLException(host, port, 'Cancelled by user')
            
    def should_trust(self, host, port):
        
        if self.ssl_error == 'Consent':
            
            return ask('Proceed to ' + host + ':' + str(port) + '?')
        
        elif self.ssl_error == 'Trust':
            
            return True
        
        else:
            
            raise SSLException(host, port, 'Configuration file requires the use of trusted certificates')
            
    def trust(self, host, port):
        
        self.tls_handler = TLSHandler( (host, port) )
            
        self.initialize_httpclient()
                    
    def increment(self):
        
        self.attempt = self.attempt + 1
        
    def reset(self):
        
        self.attempt = -1
        
class HTTPClient(AbstractHTTPClient):
    
    def __init__(self):
        
        AbstractHTTPClient.__init__(self)
    
    def get(self, uri, params = {}, headers = {}):
        
        params = urllib.parse.urlencode(params)
        
        if params:
            
            uri = uri + '?' + params
        
        request = GetRequest(uri, headers = headers)
        
        return self.dispatch(request)
            
    def post(self, uri, headers = {}, data = '', urlencode = False):
        
        if urlencode:
            
            data = urllib.parse.urlencode(data).encode('utf-8')
        
        request = PostRequest(uri, data, headers)
        
        return self.dispatch(request)
        
    def put(self, uri, headers = {}, data = ''):
    
        request = PutRequest(uri, data, headers)
        
        return self.dispatch(request)
        
    def delete(self, uri, headers = {}):
        
        request = DeleteRequest(uri, headers = headers)
        
        return self.dispatch(request)
    
    def mkcol(self, uri, headers = {}):
        
        request = MkColRequest(uri, headers = headers)
        
        return self.dispatch(request)
            
    def dispatch_request(self, request):
        
        return self.httpclient.open(request, timeout = self.timeout)