from . import uri


class DefaultBuilder:

    def __init__(self, base=None):
        self._base = base

    def __call__(self, url):
        return uri.join(self._base, url)


class EndpointBuilder(DefaultBuilder):

    def __init__(self, base, *segments):
        super().__init__(base)
        self._segments = segments

    def __call__(self, *segments):
        return uri.create(self._base, *(self._segments + segments))

    @staticmethod
    def new(base, *segments):
        return EndpointBuilder(base, *segments)
