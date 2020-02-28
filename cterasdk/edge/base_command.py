class BaseCommand:
    """ Base class for all Gateway API classes """

    def __init__(self, gateway):
        self._gateway = gateway

    def session(self):
        return self._gateway.session()
