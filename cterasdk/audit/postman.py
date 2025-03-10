import re
import uuid
import atexit
import cterasdk.settings
from ..lib import FileSystem
from ..common import Object, utf8_decode, utf8_encode
from ..convert import fromjsonstr, fromxmlstr, tojsonstr, toxmlstr
from ..objects import uri


class Collection(Object):
    """Postman Collection"""

    __instance = None

    def __init__(self):
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
        self.name = f'{str(uuid.uuid4())}'
        self.schema = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"


class Command(Object):

    def __init__(self, name, request):
        self.name = name
        self.request = request
        self.response = []


class Request(Object):

    def __init__(self, method, url):
        self.method = method
        self.header = None
        self.url = url

    def headers(self, d):
        self.header = [Header(k, v) for k, v in d.items()]

    def body(self, data):
        self.body = data


class Header(Object):

    def __init__(self, key, value):
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
                            form.add(k, v, 'text')
                        return form
                elif mime_type == 'text/plain':
                    return Raw.xml(toxmlstr(fromxmlstr(self.data), no_log=True))
                elif mime_type == 'application/json':
                    return Raw.json(tojsonstr(fromjsonstr(self.data)))
                elif mime_type.startswith('multipart/form-data'):
                    return form_data_generator(self.data, mime_type)
        return None


def form_data_generator(data, mime_type):
    boundary = re.search(r'(?<=boundary=)[A-Za-z0-9]+', mime_type).group()
    keys = [utf8_decode(key) for key in re.findall(b'(?<=\ name=")[^"]+', data)]
    if keys:
        form_data = FormData()
        segments = data.split(utf8_encode(f'--{boundary}'))
        for index, key in enumerate(keys):
            value = re.search(utf8_encode(f'(?<="{key}").+$'), segments[index + 1], re.DOTALL).group().strip()
            form_data.add(key, value)
        return form_data


class Body(Object):
    """Request Body"""

    def __init__(self, mode):
        self.mode = mode


class Form(Body):

    def __init__(self):
        super().__init__('urlencoded')
        self.urlencoded = []

    def add(self, key, value, type):
        param = Object()
        param.key = key
        param.value = value
        param.type = type
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
        self.raw = utf8_decode(body)
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
        self.raw = raw
        self.protocol = protocol
        self.host = host
        self.port = port
        self.path = [uri.quote(part) for part in path]
        self.query = query


import atexit

@atexit.register
def audit():
    if cterasdk.settings.sessions.management.audit.postman.enabled:
        fs = FileSystem.instance()
        collection = Collection.instance()
        name = cterasdk.settings.sessions.management.audit.postman.name
        if name is not None:
            collection.info.name = name
        fs.save(fs.downloads_directory(), f'{name}.json', collection.serialize().encode('utf-8'))