from ...lib import Iterator, Command

from ...common import Object

import logging

class FetchResourcesParam(Object):
    
    def __init__(self):
        
        self._classname = 'FetchResourcesParam'
        
        self.start = 0
        
        self.limit = 100
        
    def increment(self):
    
        self.start = self.start + self.limit
        
class FetchResourcesParamBuilder:
    
    def __init__(self):
        
        self.param = FetchResourcesParam()
    
    def root(self, root):
        
        self.param.root = root
        
        return self
    
    def depth(self, depth):
        
        self.param.depth = depth
        
        return self
    
    def build(self):
        
        return self.param

def list_dir(ctera_host, param):
    
    response = ctera_host.execute('', 'fetchResources', param)

    return (response.hasMore, response.items)

def ls(ctera_host, path):
    
    param = FetchResourcesParamBuilder().root(path.encoded_fullpath()).depth(1).build()
    
    function = Command(list_dir, ctera_host)
    
    return Iterator(function, param)
    