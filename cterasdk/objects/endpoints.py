from . import uri


class EndpointBuilder:

    def __init__(self, base, *segments):
        self._base = base
        self._segments = segments

    def __call__(self, *segments):
        return uri.create(self._base, *(self._segments + segments))

    @staticmethod
    def new(base, *segments):
        return EndpointBuilder(base, *segments)
