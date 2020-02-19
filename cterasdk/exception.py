from .convert import tojsonstr

class CTERAException(Exception):

    def __init__(self, message = None, instance = None, **kwargs):

        self.classname = self.__class__.__name__
    
        self.join(instance)
    
        if message != None:
            
            self.message = message
        
        self.put(**kwargs)
        
    def put(self, **kwargs):
        
        for key, value in kwargs.items():
            
            setattr(self, key, value)
        
    def join(self, instance = None):
        
        if instance != None:
            
            self.__dict__ = instance.__dict__.copy()
            
    def __str__(self):
        
        return tojsonstr(self)
    
class CTERAClientException(CTERAException):
    
    pass

class ConnectionError(CTERAException):

    def __init__(self, message, instance, host, port, protocol):
        
        CTERAException.__init__(self, message, instance, host = host, port = port, protocol = protocol)
        
class ConnectionTimeout(CTERAException):
    
    def __init__(self, message, seconds):
        
        CTERAException.__init__(self, message, None, seconds = seconds)
        
class HostUnreachable(ConnectionError):
    
    def __init__(self, instance, host, port, protocol):
        
        ConnectionError.__init__(self, "Unable to reach host", instance, host = host, port = port, protocol = protocol)
        
class ExhaustedException(ConnectionTimeout):
    
    def __init__(self, retries, timeout):
        
        ConnectionTimeout.__init__(self, "Don't blame me for lack of trying", retries * timeout)
        
        self.put(retries = retries, timeout = timeout)
        
class PythonVersionException(CTERAException):

    def __init__(self, version):
        
        CTERAException.__init__(self, 'You are running an unsupported version of Python', None, version = version)
        
class SSLException(ConnectionError):

    def __init__(self, host, port, reason):
        
        ConnectionError.__init__(self, 'Untrusted security certificate', None, host = host, port = port, protocol = 'TLS')
        
        self.put(reason = reason)
        
class ParserException(CTERAException):

    def __init__(self, fmt, payload):
        
        CTERAException.__init__(self, 'Conversion falied', None, fmt = fmt, to = 'Python Object', payload = payload)

class InputError(CTERAException):

    def __init__(self, message, expression, options):
        
        CTERAException.__init__(self, message, None, expression = expression, options = options)
        
class ConsentException(CTERAException):
    
    def __init__(self):
        
        CTERAException.__init__(self, 'Every decision is liberating, even if it leads to disaster')
        
class FileSystemException(CTERAException):
    
    pass

class RenameException(FileSystemException):
    
    def __init__(self, dirpath, src, dst):
        
        FileSystemException.__init__(self, 'Could not rename file', None, dirpath = dirpath, src = src, dst = dst)
        
class LocalDirectoryNotFound(FileSystemException):
    
    def __init__(self, path):
        
        FileSystemException.__init__(self, 'Could not find local directory', None, path = path)