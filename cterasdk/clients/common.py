from . import async_requests
from ..convert import tojsonstr, toxmlstr, fromjsonstr, fromxmlstr


class Serializers:
    JSON = tojsonstr
    XML = toxmlstr
    FormData = async_requests.FormData


class Deserializers:
    JSON = fromjsonstr
    XML = fromxmlstr


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
