from datetime import datetime

from ..lib import Iterator, Command
from ..common import Object
from ..convert import tojsonstr


def query(CTERAHost, path, param):
    response = CTERAHost.db(path, 'query', param)
    return (response.hasMore, response.objects)


def show(CTERAHost, path, param):
    hasMore, objects = query(CTERAHost, path, param)
    print(tojsonstr(objects, no_log=False))
    return hasMore


def iterator(CTERAHost, path, param):
    function = Command(query, CTERAHost, path)
    return Iterator(function, param)


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

    @staticmethod
    def fromValue(value):
        if isinstance(value, datetime):
            return FilterType.DateTime
        if isinstance(value, bool):
            return FilterType.Boolean
        if isinstance(value, int):
            return FilterType.Integer
        if isinstance(value, str):
            return FilterType.String
        raise TypeError("value must be of one of the following types: datetime, bool, int or str")


class Filter(Object):

    def __init__(self, field):
        self.field = field


class FilterBuilder(Object):

    def __init__(self, name):
        self.filter = Filter(name)

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
        self.filter._classname = FilterType.fromValue(value)  # pylint: disable=protected-access,attribute-defined-outside-init
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
