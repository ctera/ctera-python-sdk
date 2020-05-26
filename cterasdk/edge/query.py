from ..common import Object
from ..convert import tojsonstr


def query(CTERAHost, path, key, value):
    param = Object()
    param.key = key
    param.value = value
    return CTERAHost.db(path, 'query', param)


def show(CTERAHost, path, key, value):
    print(tojsonstr(query(CTERAHost, path, key, value), no_log=False))


class QueryParam(Object):

    def __init__(self):
        self.startFrom = 0
        self.countLimit = 50

    def include_classname(self):
        self._classname = self.__class__.__name__  # pylint: disable=attribute-defined-outside-init

    def increment(self):
        self.startFrom = self.startFrom + self.countLimit


class QueryParamBuilder:

    def __init__(self):
        self.param = QueryParam()

    def startFrom(self, startFrom):
        self.param.startFrom = startFrom
        return self

    def countLimit(self, countLimit):
        self.param.countLimit = countLimit
        return self

    def include(self, include):
        self.param.include = include  # pylint: disable=attribute-defined-outside-init
        return self

    def put(self, key, value):
        setattr(self.param, key, value)
        return self

    def build(self):
        return self.param
