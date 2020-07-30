import urllib.parse
import logging

import requests
import requests.exceptions as requests_exceptions
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

# from .ssl import CertificateServices
from ..convert import fromxmlstr
from ..common import Object
from .. import config
from ..exception import SSLException, HostUnreachable, ExhaustedException
from ..lib import ask


class HTTPException(Exception):

    def __init__(self, http_error):
        super().__init__()
        self.response = Object()
        self.response.code = http_error.response.status_code
        self.response.reason = http_error.response.reason
        self.response.body = fromxmlstr(http_error.response.text)
        if config.http['verbose']:
            self.response.headers = http_error.response.headers
            self.request = HTTPException._parse_request(http_error.request)

    @staticmethod
    def _parse_request(request):
        o = urllib.parse.urlparse(request.url)
        target = Object()
        target.host = Object()
        target.host.scheme = o.scheme
        target.host.hostname = o.hostname
        target.host.port = o.port
        target.method = request.method
        target.uri = o.path
        target.headers = request.headers
        if request.body is not None:
            target.body = request.body.decode('utf-8')  # decode from 'Bytes' to 'UTF-8'
        return target


class HTTPResponse:

    def __init__(self, response):
        self.url = response.url
        self.code = response.status_code
        self.headers = response.headers
        self.text = response.text

    def geturl(self):
        return self.url

    def getcode(self):
        return self.code

    def read(self):
        return self.text


def geturi(baseurl, path):
    path = urllib.parse.quote(path)
    count = int(baseurl.endswith('/')) + int(path.startswith('/'))
    if count == 2:
        return baseurl[:-1] + path
    if count == 1:
        return baseurl + path
    if count == 0:
        return baseurl + '/' + path
    raise ValueError("Invalid baseurl/path combination")


class ContentType:
    urlencoded = {'Content-Type': 'application/x-www-form-urlencoded'}
    textplain = {'Content-Type': 'text/plain'}


class HttpClientBase():
    def __init__(self, session_id_key):
        self.timeout = config.http['timeout']
        self.retries = config.http['retries']
        self.ssl_error_handling = config.http['ssl']
        self.session = requests.Session()
        self.session.verify = self.ssl_error_handling != 'Trust'
        self._session_id_key = session_id_key

    def dispatch(self, ctera_request):
        attempt = 0
        while attempt < self.retries:
            try:
                return self._do_dispatch(ctera_request)
            except requests_exceptions.HTTPError as error:
                raise HTTPException(error)
            except requests_exceptions.Timeout:
                self.on_timeout(attempt)
            except requests_exceptions.SSLError as error:
                self.on_ssl_error(error.request)
                attempt = -1
            except requests_exceptions.ConnectionError as error:
                self._on_unreachable(error)
            except requests_exceptions.RequestException as error:
                logging.getLogger().warning(error)
            attempt = attempt + 1
        logging.getLogger().error('Reached maximum number of retries. %s', {'retries': self.retries, 'timeout': self.timeout})
        raise ExhaustedException(self.retries, self.timeout)

    def _do_dispatch(self, ctera_request):
        response = self.session.request(ctera_request.method, ctera_request.url, **ctera_request.kwargs)
        response.raise_for_status()
        return (response.request, response)

    @staticmethod
    def _on_unreachable(error):
        parsed_url = urllib.parse.urlparse(error.request.url)
        logging.getLogger().error('Cannot reach target host. %s', {'host': parsed_url.hostname, 'port': parsed_url.port})
        socket_error = Object()
        socket_error.message = str(error)
        raise HostUnreachable(socket_error, parsed_url.hostname, parsed_url.port, parsed_url.scheme.upper())

    @staticmethod
    def on_timeout(attempt):
        logging.getLogger().warning('Request timed out. %s', {'attempt': (attempt + 1)})

    def on_ssl_error(self, request):
        parsed_url = urllib.parse.urlparse(request.url)
        if self.should_trust(parsed_url.hostname, parsed_url.port):
            self.trust(parsed_url.hostname, parsed_url.port)
        else:
            raise SSLException(parsed_url.hostname, parsed_url.port, 'Cancelled by user')

    def should_trust(self, host, port):
        if self.ssl_error_handling == 'Consent':
            return ask('Proceed to ' + host + ':' + str(port) + '?')
        raise SSLException(host, port, 'Configuration file requires the use of trusted certificates')

    def trust(self, _host, _port):
        self.session.verify = False  # CertificateServices.save_cert_from_server(host, port)

    def get_session_id(self):
        return self.session.cookies.get(self._session_id_key)

    def set_session_id(self, session_id):
        self.session.cookies.set(self._session_id_key, session_id)


class HttpClientRequest():
    def __init__(self, method, url, **kwargs):
        self.method = method
        self.url = url
        self.kwargs = kwargs


class HttpClientRequestGet(HttpClientRequest):
    def __init__(self, url, params=None, headers=None, stream=None):
        super().__init__('GET', url, params=params, headers=headers, stream=stream)


class HttpClientRequestPost(HttpClientRequest):
    def __init__(self, url, headers=None, data=None):
        super().__init__('POST', url, headers=headers, data=data)


class HttpClientRequestPut(HttpClientRequest):
    def __init__(self, url, headers=None, data=None):
        super().__init__('PUT', url, headers=headers, data=data)


class HttpClientRequestDelete(HttpClientRequest):
    def __init__(self, url, headers=None):
        super().__init__('DELETE', url, headers=headers)


class HttpClientRequestMkcol(HttpClientRequest):
    def __init__(self, url, headers=None):
        super().__init__('MKCOL', url, headers=headers)


class HTTPClient(HttpClientBase):

    def get(self, url, params=None, headers=None, stream=None):
        return self.dispatch(HttpClientRequestGet(url, params=params, headers=headers, stream=stream))

    def post(self, url, headers=None, data='', urlencode=False):
        if urlencode:
            data = urllib.parse.urlencode(data).encode('utf-8')
        return self.dispatch(HttpClientRequestPost(url, headers=headers, data=data))

    def put(self, url, headers=None, data=''):
        return self.dispatch(HttpClientRequestPut(url, headers=headers, data=data))

    def delete(self, url, headers=None):
        return self.dispatch(HttpClientRequestDelete(url, headers=headers))

    def mkcol(self, url, headers=None):
        return self.dispatch(HttpClientRequestMkcol(url, headers=headers))

    def multipart(self, url, form_data, monitor_function_generator=None):
        encoder = MultipartEncoder(form_data)
        if monitor_function_generator:
            encoder = MultipartEncoderMonitor(encoder, callback=monitor_function_generator(encoder.len))
        return self.dispatch(HttpClientRequestPost(url, headers={'Content-Type': encoder.content_type}, data=encoder))

    def upload(self, url, form_data):
        def upload_monitor_generator(total_length):
            def upload_monitor(encoder):
                logging.getLogger().info(
                    'Uploaded %(percent)s - (%(uploaded)s out of %(size)s)',
                    dict(
                        percent=str(round(encoder.bytes_read/total_length*100))+'%',
                        uploaded=encoder.bytes_read,
                        size=total_length
                    )
                )
            return upload_monitor
        return self.multipart(url, form_data, upload_monitor_generator)
