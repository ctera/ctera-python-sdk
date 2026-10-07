class CTERAException(Exception):
    """
    Base Exception.

    :param str message: Error message
    :ivar str reason: Portal error message from :attr:`~BaseException.__cause__` when it is an HTTP transport error
    """
    def __init__(self, message=None, **kwargs):
        super().__init__(message)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def reason(self):
        cause = self.__cause__
        if cause is None:
            return None
        error_object = getattr(cause, 'error', None)
        if error_object is None:
            return None
        response = getattr(error_object, 'response', None)
        portal_error = getattr(response, 'error', None) if response else None
        if portal_error is None or isinstance(portal_error, str):
            return None
        return getattr(portal_error, 'msg', None)

    def __repr__(self):
        return str(self)
