from abc import abstractmethod


class CTERAException(Exception):
    """
    Base Exception.

    :param str message: Error message
    :ivar str reason: Server error message
    """
    def __init__(self, message=None, **kwargs):
        super().__init__(message)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    @abstractmethod
    def reason(self):
        return self.__cause__.reason if self.__cause__ and hasattr(self.__cause__, 'reason') else None

    def __repr__(self):
        return str(self)
