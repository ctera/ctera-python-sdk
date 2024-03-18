class BaseCommand:
    """Base Class for CTERA Portal API Commands"""

    def __init__(self, core):
        self._core = core
