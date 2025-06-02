from abc import ABC, abstractmethod
from http import HTTPStatus
from ..exceptions import HTTPError
from ..common import Object
from ..convert import fromjsonstr, fromxmlstr


class Error(Object):
    """
    Error object.

    :ivar cterasdk.common.object.Object request: Request
    :ivar cterasdk.common.object.Object response: Response
    """
    def __init__(self, response, error):
        super().__init__(
            request=Object(
                method=response.method,
                url=response.real_url.human_repr()
            ),
            response=Object(
                status=response.status,
                error=error
            )
        )


class ErrorHandler(ABC):

    async def a_accept(self, response):
        error = self._accept(response, await response.text())
        raise_error(response.status, error)

    def accept(self, response):
        error = self._accept(response, response.text())
        raise_error(response.status, error)

    @abstractmethod
    def _accept(self, response, message):
        raise NotImplementedError("Subclass must implement the '_accept' method")


class DefaultHandler(ErrorHandler):

    def _accept(self, response, message):
        return Error(response, message)


class XMLHandler(ErrorHandler):

    def _accept(self, response, message):
        return Error(response, fromxmlstr(message) or message)


class JSONHandler(ErrorHandler):

    def _accept(self, response, message):
        return Error(response, fromjsonstr(message) or message)


class BadRequest(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.BAD_REQUEST, error)


class Unauthorized(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.UNAUTHORIZED, error)


class Forbidden(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.FORBIDDEN, error)


class NotFound(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.NOT_FOUND, error)


class Unprocessable(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, error)


class InternalServerError(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, error)


class BadGateway(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.BAD_GATEWAY, error)


class ServiceUnavailable(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.SERVICE_UNAVAILABLE, error)


class GatewayTimeout(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.GATEWAY_TIMEOUT, error)


def raise_error(status, error):
    exceptions = {
        HTTPStatus.BAD_REQUEST: BadRequest,
        HTTPStatus.UNAUTHORIZED: Unauthorized,
        HTTPStatus.FORBIDDEN: Forbidden,
        HTTPStatus.NOT_FOUND: NotFound,
        HTTPStatus.UNPROCESSABLE_ENTITY: Unprocessable,
        HTTPStatus.INTERNAL_SERVER_ERROR: InternalServerError,
        HTTPStatus.BAD_GATEWAY: BadGateway,
        HTTPStatus.SERVICE_UNAVAILABLE: ServiceUnavailable,
        HTTPStatus.GATEWAY_TIMEOUT: GatewayTimeout
    }
    exception = exceptions.get(status, HTTPError)
    raise exception(error)
