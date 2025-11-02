class CTERAException(Exception):
    """
    Base Exception.

    :parm str message: Error message
    """
    def __init__(self, message=None, **kwargs):
        super().__init__(message)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return str(self)
