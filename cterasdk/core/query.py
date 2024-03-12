from datetime import datetime

from ..lib import QueryIterator, DefaultResponse, Command
from ..common import Object


def create_callback_function(core, path, name=None, *, callback_response=None):
    """
    Create a query callback function

    :param cterasdk.objects.core.Portal core: Portal object
    :param cterasdk.core.query.QueryParams param: Query paramter object
    :param str,optional name: Schema method name
    :param cterasdk.lib.iterator.BaseResponse callback_response: Class to consume callback response

    :returns: Command object
    """

    def database(core, path, name, param):
        return callback_response(core.api.database(path, name, param))

    def execute(core, path, name, param):
        return callback_response(core.api.execute(path, name, param))

    return Command(execute if name else database, core, path, name or 'query')


def iterator(core, path, param=None, name=None, *, callback_response=None):
    """
    Create iterator

    :param cterasdk.objects.core.Portal core: Portal object
    :param str path: URL Path
    :param str,optional name: Schema method name
    :param cterasdk.core.query.QueryParams,optional param: Query paramter object
    :param cterasdk.lib.iterator.BaseResponse callback_response: Class to consume callback response

    :returns: Query iterator object
    """

    callback_response = callback_response if callback_response else DefaultResponse
    callback_function = create_callback_function(core, path, name, callback_response=callback_response)
    return QueryIterator(callback_function, param if param else QueryParams())


class Restriction:
    LIKE = "like"
    UNLIKE = "notLike"
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_EQUALS = "ge"
    GREATER_THAN = "gt"
    LESS_EQUALS = "le"
    LESS_THAN = "lt"


class FilterType:

    DateTime = 'DateTimeFilter'
    Boolean = 'BooleanFilter'
    Integer = 'IntFilter'
    String = 'StringFilter'
    RefFilter = 'RefFilter'
    IntRefFilter = 'IntRefFilter'
    BooleanRefFilter = 'BooleanRefFilter'

    @staticmethod
    def fromValue(value, ref):
        if isinstance(value, datetime):
            return FilterType.DateTime
        if isinstance(value, bool):
            return FilterType.BooleanRefFilter if ref else FilterType.Boolean
        if isinstance(value, int):
            return FilterType.IntRefFilter if ref else FilterType.Integer
        if isinstance(value, str):
            return FilterType.RefFilter if ref else FilterType.String
        raise TypeError("value must be of one of the following types: datetime, bool, int or str")


class Filter(Object):

    def __init__(self, field):
        self.field = field


class FilterBuilder(Object):

    def __init__(self, name, reference=False):
        self.filter = Filter(name)
        self.reference = reference

    @staticmethod
    def ref(name):
        return FilterBuilder(name, True)

    def like(self, value):
        self.filter.restriction = Restriction.LIKE  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def notLike(self, value):
        self.filter.restriction = Restriction.UNLIKE  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def eq(self, value):
        self.filter.restriction = Restriction.EQUALS  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def ne(self, value):
        self.filter.restriction = Restriction.NOT_EQUALS  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def ge(self, value):
        self.filter.restriction = Restriction.GREATER_EQUALS  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def gt(self, value):
        self.filter.restriction = Restriction.GREATER_THAN  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def le(self, value):
        self.filter.restriction = Restriction.LESS_EQUALS  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def lt(self, value):
        self.filter.restriction = Restriction.LESS_THAN  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def before(self, value):
        self.filter.restriction = Restriction.LESS_THAN  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def after(self, value):
        self.filter.restriction = Restriction.GREATER_THAN  # pylint: disable=attribute-defined-outside-init
        return self.setValue(value)

    def setValue(self, value):
        self.filter._classname = FilterType.fromValue(value, self.reference)  # pylint: disable=protected-access,W0201
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%dT%H:%M:%S')
        self.filter.value = value  # pylint: disable=attribute-defined-outside-init

        return self.filter


class QueryParams(Object):

    def __init__(self):
        self.startFrom = 0
        self.countLimit = 50

    def include_classname(self):
        self._classname = self.__class__.__name__  # pylint: disable=attribute-defined-outside-init

    def increment(self):
        self.startFrom = self.startFrom + self.countLimit


class QueryParamBuilder:

    def __init__(self):
        self.param = QueryParams()

    def include_classname(self):
        self.param.include_classname()
        return self

    def startFrom(self, startFrom):
        self.param.startFrom = startFrom
        return self

    def countLimit(self, countLimit):
        self.param.countLimit = countLimit
        return self

    def include(self, include):
        self.param.include = include  # pylint: disable=attribute-defined-outside-init
        return self

    def addFilter(self, query_filter):
        if not hasattr(self.param, 'filters'):
            self.param.filters = []  # pylint: disable=attribute-defined-outside-init
        self.param.filters.append(query_filter)
        return self

    def orFilter(self, orFilter):
        self.param.orFilter = orFilter  # pylint: disable=attribute-defined-outside-init
        return self

    def sortBy(self, sortBy):
        self.param.sortBy = sortBy  # pylint: disable=attribute-defined-outside-init
        return self

    def allPortals(self, allPortals):
        self.param.allPortals = allPortals  # pylint: disable=attribute-defined-outside-init
        return self

    def ownedBy(self, ownedBy):
        self.param.ownedBy = ownedBy  # pylint: disable=attribute-defined-outside-init
        return self

    def put(self, key, value):
        setattr(self.param, key, value)
        return self

    def build(self):
        return self.param
