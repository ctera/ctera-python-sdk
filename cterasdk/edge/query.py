from ..lib import QueryIterator, DefaultResponse, KeyValueQueryIterator, Command
from ..common import Object


def create_callback_function(edge, path, name=None, *, callback_response=None):
    """
    Create a query callback function

    :param cterasdk.objects.core.Portal core: Portal object
    :param cterasdk.edge.query.QueryParam param: Query paramter object
    :param str,optional name: Schema method name

    :returns: Command object
    """

    def database(edge, path, name, param):
        return edge.api.database(path, name, param)

    def execute(edge, path, name, param):
        response_consumer = callback_response if callback_response else DefaultResponse
        return response_consumer(edge.api.execute(path, name, param))

    return Command(execute if name else database, edge, path, name or 'query')


def iterator(edge, path, param=None, name=None, callback_response=None):
    """
    Create iterator

    :param cterasdk.objects.edge.Edge edge: Edge object
    :param str path: URL Path
    :param str,optional name: Schema method name
    :param cterasdk.edge.query.QueryParam,optional param: Query paramter object
    :param cterasdk.lib.iterator.BaseResponse callback_response: Class to consume callback response

    :returns: Query iterator object
    """
    object_iterator = QueryIterator if name else KeyValueQueryIterator
    callback_function = create_callback_function(edge, path, name, callback_response=callback_response)
    return object_iterator(callback_function, param if param else QueryParam())


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
