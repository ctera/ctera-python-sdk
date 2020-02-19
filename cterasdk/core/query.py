from ..lib import Iterator, Command

from ..common import Object

from ..convert import tojsonstr

from datetime import datetime

def query(CTERAHost, path, param):
                
    response = CTERAHost.db(CTERAHost._api(), path, 'query', param)
    
    return (response.hasMore, response.objects)

def show(CTERAHost, path, param):
    
    hasMore, objects = query(CTERAHost, path, param)
    
    print(tojsonstr(objects))
    
    return hasMore
 
def iterator(CTERAHost, path, param):
    
    function = Command(CTERAHost.query, path)
        
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
    
    @staticmethod
    def fromValue(value):
        
        if isinstance(value, datetime):
            
            return 'DateTimeFilter'
        
        elif type(value) == bool:
            
            return 'BooleanFilter'
        
        elif type(value) == int:
            
            return 'IntFilter'
        
        elif type(value) == str:
            
            return 'StringFilter'

class Filter(Object):
    
    def __init__(self, field):
        
        self.field = field

class FilterBuilder(Object):
    
    def __init__(self, name):
        
        self.filter = Filter(name)
        
    def like(self, value):
        
        self.filter.restriction = Restriction.LIKE
        
        return self.setValue(value)
        
    def notLike(self, value):
        
        self.filter.restriction = Restriction.UNLIKE
        
        return self.setValue(value)
        
    def eq(self, value):
        
        self.filter.restriction = Restriction.EQUALS
        
        return self.setValue(value)
        
    def ne(self, value):
        
        self.filter.restriction = Restriction.NOT_EQUALS
        
        return self.setValue(value)
        
    def ge(self, value):
        
        self.filter.restriction = Restriction.GREATER_EQUALS
        
        return self.setValue(value)
        
    def gt(self, value):
        
        self.filter.restriction = Restriction.GREATER_THAN
        
        return self.setValue(value)
        
    def le(self, value):
        
        self.filter.restriction = Restriction.LESS_EQUALS
        
        return self.setValue(value)
        
    def lt(self, value):
        
        self.filter.restriction = Restriction.LESS_THAN
        
        return self.setValue(value)
    
    def before(self, value):
        
        self.filter.restriction = Restriction.LESS_THAN
        
        return self.setValue(value)
    
    def after(self, value):
        
        self.filter.restriction = Restriction.GREATER_THAN
        
        return self.setValue(value)
        
    def setValue(self, value):
        
        self.filter._classname = FilterType.fromValue(value)
        
        if isinstance(value, datetime):
        
            value = value.strftime('%Y-%m-%dT%H:%M:%S')
        
        self.filter.value = value

        return self.filter

class QueryParams(Object):
    
    def __init__(self):
        
        self.startFrom = 0
        
        self.countLimit = 50
        
    def include_classname(self):
        
        self._classname = self.__class__.__name__
        
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
    
        self.param.include = include
        
        return self
    
    def addFilter(self, filter):
        
        if not hasattr(self.param, 'filters'):
            
            self.param.filters = []
        
        self.param.filters.append(filter)
        
        return self
        
    def orFilter(self, orFilter):
    
        self.param.orFilter = orFilter
        
        return self
        
    def sortBy(self, sortBy):
    
        self.param.sortBy = sortBy
        
    def allPortals(self, allPortals):
        
        self.param.allPortals = allPortals
        
        return self
    
    def put(self, key, value):
        
        setattr(self.param, key, value)
        
        return self
        
    def build(self):
    
        return self.param