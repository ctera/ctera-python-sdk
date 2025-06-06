class CTERAException(Exception):
    """
    Base Exception.

    :parm str message: Error message
    """
    def __init__(self, message=None):
        super().__init__(message)

    def __repr__(self):
        return str(self)
