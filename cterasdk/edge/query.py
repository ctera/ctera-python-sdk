from ..lib import Iterator, Command

from ..common import Object

from ..convert import tojsonstr
    
def query(CTERAHost, path, key, value):
    
    param = Object()
        
    param.key = key

    param.value = value
                
    return CTERAHost.db(CTERAHost._api(), path, 'query', param)

def show(CTERAHost, path, key, value):
    
    print(tojsonstr(query(CTERAHost, path, key, value)))
    
class QueryParam(Object):
    
    def __init__(self):
        
        self.startFrom = 0
        
        self.countLimit = 50
        
    def include_classname(self):
        
        self._classname = self.__class__.__name__
        
    def increment(self):
    
        self.startFrom = self.startFrom + self.countLimit

class QueryParamBuilder:

    def __init__(self):
    
        self.param = QueryParam()
        
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