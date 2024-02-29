class BaseCommand:
    """ Base class for all Gateway API classes """

    def __init__(self, edge):
        self._edge = edge

    def session(self):
        return self._edge.session()
