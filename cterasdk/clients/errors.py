import aiohttp

from ..common import Object
from ..convert import fromjsonstr, fromxmlstr
from ..exceptions import ClientResponseException


class ClientError(Object):

    def __init__(self, exception, message):
        self.request = Object()
        self.request.method = exception.request_info.method
        self.request.url = str(exception.request_info.real_url)
        self.response = Object()
        self.response.status = exception.status
        self.response.message = fromxmlstr(message) or fromjsonstr(message) or message


def accept(response, error_message):
    try:
        response.raise_for_status()
    except aiohttp.ClientResponseError as exception:
        error_object = ClientError(exception, error_message)
        raise ClientResponseException(error_object)
    return response
