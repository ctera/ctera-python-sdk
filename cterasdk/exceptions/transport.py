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
    """
    Bad Request

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.BAD_REQUEST, error)


class Unauthorized(HTTPError):
    """
    Unauthorized

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.UNAUTHORIZED, error)


class Forbidden(HTTPError):
    """
    Unauthorized

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.FORBIDDEN, error)


class NotFound(HTTPError):
    """
    NotFound

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.NOT_FOUND, error)


class Unprocessable(HTTPError):
    """
    Unprocessable

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, error)


class InternalServerError(HTTPError):
    """
    InternalServerError

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, error)


class BadGateway(HTTPError):
    """
    BadGateway

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.BAD_GATEWAY, error)


class ServiceUnavailable(HTTPError):
    """
    ServiceUnavailable

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.SERVICE_UNAVAILABLE, error)


class GatewayTimeout(HTTPError):
    """
    GatewayTimeout

    :ivar int code: Status code
    :ivar str name: Reason
    :ivar cterasdk.clients.errors.Error error: Error object
    """

    def __init__(self, error):
        super().__init__(HTTPStatus.GATEWAY_TIMEOUT, error)
