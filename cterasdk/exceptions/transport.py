from http import HTTPStatus
from .base import CTERAException


class HTTPError(CTERAException):
    """
    HTTP Error

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, status, error):
        super().__init__(error.request.url)
        self.code = status.value
        self.name = status.name
        self.error = error


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


class NotAllowed(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.METHOD_NOT_ALLOWED, error)


class PreConditionFailed(HTTPError):

    def __init__(self, error):
        super().__init__(HTTPStatus.PRECONDITION_FAILED, error)


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


class TLSError(CTERAException):
    """
    TLS Error

    :ivar str host: Host
    :ivar int port: Port
    """

    def __init__(self, host, port):
        super().__init__(f"TLS handshake to '{host}:{port}' failed.")
        self.host = host
        self.port = port
