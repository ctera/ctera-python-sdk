class BaseCommand:
    """Base Class for CTERA Edge Filer API Commands"""

    def __init__(self, edge):
        self._edge = edge

    def session(self):
        return self._edge.session()
