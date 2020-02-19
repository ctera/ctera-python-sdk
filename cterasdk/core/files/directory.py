import logging

from ...common import Object

from ...exception import CTERAException

from .path import CTERAPath

class ItemExists(CTERAException):
    
    pass

class InvalidPath(CTERAException):
    
    pass

class InvalidName(CTERAException):
    
    pass

class ReservedName(CTERAException):
    
    pass

FileManagerTaskRC = {
    
    "FileWithTheSameNameExist" : ItemExists,
    
    "DestinationNotExists" : InvalidPath,
    
    "InvalidName" : InvalidName,
    
    "ReservedName" : ReservedName
    
}

def mkdir(ctera_host, path, recurse = False):
    
    if recurse:
        
        array = path.parts()

        for i in range(1, len(array) + 1):
            
            dirpath = CTERAPath('/'.join(array[:i]), path.basepath)

            try:

                _mkdir(ctera_host, dirpath)

            except ItemExists:

                pass
            
    else:
        
        _mkdir(ctera_host, path)

def _mkdir(ctera_host, path):
    
    filename    = path.name()
    
    parent      = path.encoded_parent()
    
    param               = Object()
    
    param.name          = path.name()
    
    param.parentPath    = path.parent().encoded_fullpath()
    
    relativepath = str(path.relativepath)
    
    logging.getLogger().info('Creating directory. {0}'.format({'path' : relativepath}))
    
    response = ctera_host.execute('', 'makeCollection', param)
    
    _process_response(response, relativepath)

def _process_response(response, path):
    
    try:
    
        _process_error(response, path)
        
    except ItemExists as error:
        
        logging.getLogger().warn('A file or folder with the same name already exists. {0}'.format({'path' : path}))
        
        raise error
        
    except InvalidPath as error:
        
        logging.getLogger().error('Invalid parent directory path. {0}'.format({'path' : path}))
        
        raise error
        
    except InvalidName as error:
        
        logging.getLogger().error('Directory name contains invalid characters. {0}'.format({'name' : path}))
        
        raise error
        
    except ReservedName as error:
        
        logging.getLogger().error('Reserved directory name. {0}'.format({'name' : path}))
        
        raise error
        
    else:
    
        logging.getLogger().info('Directory created. {0}'.format({'path' : path}))
    
def _process_error(response, path):
    
    error = FileManagerTaskRC.get(response)
    
    if error != None:
    
        error = error()
    
        error.path = path
            
        raise error
