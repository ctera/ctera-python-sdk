from ..exception import CTERAException

import functools

import logging

def authenticated(function):
    
    @functools.wraps(function)
    def check_authenticated_and_call(self, *args):
        
        session = self.session()
        
        if session.authenticated():
            
            return function(self, *args)
        
        elif is_nosession(function, args[0]):
            
            return function(self, *args)
        
        else:
            
            logging.getLogger().error('Not logged in.')
            
            raise CTERAException('Not logged in')
        
    return check_authenticated_and_call

def is_nosession(function, path):
    
    return (function.__name__ == 'get' and path.startswith('/nosession'))