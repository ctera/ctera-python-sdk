import re
import uuid
import atexit
import logging
import cterasdk.settings
from ..lib.storage import synfs, commonfs
from ..common import Object, utf8_decode, utf8_encode
from ..convert import fromjsonstr, fromxmlstr, tojsonstr, toxmlstr
from ..objects import uri


class Collection(Object):
    """Postman Collection"""

    __instance = None

    def __init__(self):
        super().__init__()
        self.info = Info()
        self.item = []
        Collection.__instance = self

    @staticmethod
    def instance():
        if Collection.__instance is None:
            Collection()
        return Collection.__instance

    def add(self, request):
        name = f'{request.method} /{"/".join(request.url.path)}'
        self.item.append(Command(name, request))

    def serialize(self):
        return str(self)


class Info(Object):

    def __init__(self):
        super().__init__()
        self.name = f'{str(uuid.uuid4())}'
        self.schema = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"


class Command(Object):

    def __init__(self, name, request):
        super().__init__()
        self.name = name
        self.request = request
        self.response = []


class Request(Object):

    def __init__(self, method, url):
        super().__init__()
        self.method = method
        self.header = None
        self.url = url

    def request_headers(self, d):
        self.header = [Header(k, v) for k, v in d.items()]

    def request_body(self, data):
        self.body = data  # pylint: disable=attribute-defined-outside-init


class Header(Object):

    def __init__(self, key, value):
        super().__init__()
        self.key = key
        self.value = value
        self.type = 'text'


class BodyStream:

    def __init__(self):
        self.data = bytearray()
        self.maxsize = 4194304  # 4 MB

    def append(self, data):
        if len(self.data) >= self.maxsize:
            return
        self.data = self.data + data[:self.maxsize - len(self.data)]

    def deserialize(self, mime_type):
        if self.data:
            if mime_type is not None:
                if mime_type == 'application/x-www-form-urlencoded':
                    form_data = uri.parse_qsl(utf8_decode(self.data))
                    if form_data:
                        form = Form()
                        for k, v in form_data:
                            form.add(k, v)
                        return form
                elif mime_type == 'text/plain':
                    return Raw.xml(toxmlstr(fromxmlstr(self.data), no_log=True))
                elif mime_type == 'application/json':
                    return Raw.json(tojsonstr(fromjsonstr(self.data), False))
                elif mime_type.startswith('multipart/form-data'):
                    return form_data_generator(self.data, mime_type)
        return None


def form_data_generator(data, mime_type):
    """
    Generate Form Data.

    :param bytearray data: Body.
    :param str mime_type: Header.
    """
    boundary = form_boundary(mime_type)
    keys = form_keys(data)
    if keys:
        form_data = FormData()
        segments = data.split(boundary)
        for index, key in enumerate(keys):
            value = form_value(segments[index + 1], key)
            form_data.add(key, value)
        return form_data
    return None


def form_value(data, key):
    """
    Get Value for Key.

    :param bytearray data: Segment of Body.
    :param bytes key: UTF-8 Encoded Key.
    """
    CRLF = '\r\n\r\n'
    expr = utf8_encode(f'(?<={key}"{CRLF})[^\r]+')
    match = re.search(expr, data, re.DOTALL)
    return match.group() if match else None


def form_keys(data):
    """
    Get Form Keys from Data.

    :param bytearray data: Body.
    :returns: UTF-8 Encoded Keys
    :rtype: list[bytes]
    """
    return [utf8_decode(key) for key in re.findall(rb'(?<=\ name=")[^"]+', data)]


def form_boundary(mime_type):
    """
    Get Multiparty Form Boundary from Content Type Header.

    :param str mime_type: Header.
    :returns: UTF-8 Encoded Boundary.
    :rtype: bytes
    """
    match = re.search(r'(?<=boundary=)[A-Za-z0-9]+', mime_type)
    return utf8_encode(f'--{match.group()}') if match else None


class Body(Object):
    """Request Body"""

    def __init__(self, mode):
        super().__init__()
        self.mode = mode


class Form(Body):

    def __init__(self):
        super().__init__('urlencoded')
        self.urlencoded = []

    def add(self, key, value):
        param = Object()
        param.key = key
        if key in ['j_password']:
            value = '*** Protected Value ***'
        param.value = value
        param.type = 'text'
        self.urlencoded.append(param)


class FormData(Body):

    def __init__(self):
        super().__init__('formdata')
        self.formdata = []

    def add(self, key, value):
        param = Object()
        param.key = key
        if key == 'file':
            param.type = 'file'
            param.src = ''
        else:
            param.type = 'text'
            param.value = utf8_decode(value)
        self.formdata.append(param)


class Raw(Body):

    def __init__(self, body, language):
        super().__init__('raw')
        self.raw = body if language == 'json' else utf8_decode(body)
        self.options = Object()
        self.options.raw = Object()
        self.options.language = language

    @staticmethod
    def xml(body):
        return Raw(body, 'xml')

    @staticmethod
    def json(body):
        return Raw(body, 'json')


class URL(Object):

    def __init__(self, raw, protocol, host, port, path, query):
        super().__init__()
        self.raw = raw
        self.protocol = protocol
        self.host = host
        self.port = port
        self.path = [uri.quote(part) for part in path]
        self.query = query


@atexit.register
def audit():
    if cterasdk.settings.audit.enabled:
        collection = Collection.instance()
        name = cterasdk.settings.audit.filename
        collection.info.name = name if name is not None else str(uuid.uuid4())
        filename = f'{collection.info.name}.json'
        logging.getLogger('cterasdk.http').info('Saving Postman audit file. %s', {
            'directory': commonfs.downloads(),
            'name': filename
        })
        synfs.write(commonfs.downloads(), filename, utf8_encode(collection.serialize()))
