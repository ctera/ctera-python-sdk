class BaseCommand:
    """ Base class for all Portal API classes """

    def __init__(self, core):
        self._core = core

    def session(self):
        return self._core.session()
