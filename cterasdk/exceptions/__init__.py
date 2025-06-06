from ..convert import tojsonstr


class CTERAException(Exception):
    """
    Base Exception.

    :parm str message: Error message
    """
    def __init__(self, message=None):
        super().__init__(message)

    def __repr__(self):
        return str(self)


class ObjectNotFoundException(CTERAException):
    """
    Object not found.

    :param str urn: Resource
    """

    def __init__(self, urn):
        super().__init__(f'Object not found: {urn}')


class InputError(ValueError):
    """
    Input Error

    :param str message: Error message
    :param object expression: Error expression
    :param object options: Options
    """

    def __init__(self, message, expression=None, options=None):
        super().__init__(self, message)
        self.expression = expression
        self.options = options


class UserConsentError(CTERAException):
    """Console"""


from . import (
    backup,
    direct,
    io,
    notifications,
    session,
    transport
)