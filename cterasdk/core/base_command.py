class BaseCommand:
    """ Base class for all Portal API classes """

    def __init__(self, portal):
        self._portal = portal

    def session(self):
        return self._portal.session()
