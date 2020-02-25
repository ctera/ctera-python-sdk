class BaseCommand:

    def __init__(self, gateway):
        self._gateway = gateway

    def session(self):
        return self._gateway.session()
