import aiohttp

from ..common import Object
from ..convert import fromjsonstr, fromxmlstr
from ..exceptions import ClientResponseException


class ClientError(Object):

    def __init__(self, error, message):
        self.request = Object()
        self.request.method = error.request_info.method
        self.request.url = str(error.request_info.real_url)
        self.response = Object()
        self.response.status = error.status
        self.response.message = fromxmlstr(message) or fromjsonstr(message) or message


def accept_response(response):
    message = response.text if response.status > 400 else None
    try:
        response.raise_for_status()
    except aiohttp.ClientResponseError as error:
        error_object = ClientError(error, message)
        raise ClientResponseException(error_object)
    return response
