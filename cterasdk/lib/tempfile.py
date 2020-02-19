from .registry import Registry

import logging

import tempfile

import shutil

import atexit

class TempfileServices:
    
    __tempdir_prefix = 'chopin_core-'
    
    @staticmethod
    def mkdir():
        
        registry = Registry.instance()
        
        tempdir = registry.get('tempdir')
        
        if tempdir == None:
            
            logging.getLogger().debug('Creating temporary directory.')
        
            tempdir = tempfile.mkdtemp(prefix = TempfileServices.__tempdir_prefix)
            
            logging.getLogger().debug('Temporary directory created. {0}'.format({'path' : tempdir}))

            registry.register('tempdir', tempdir)
            
        return tempdir
        
    @staticmethod
    def mkfile(prefix, suffix):
        
        tempdir = TempfileServices.mkdir()
        
        logging.getLogger().debug('Creating temporary file.')
        
        fd, filepath = tempfile.mkstemp(prefix = prefix, suffix = suffix, dir = tempdir)
        
        logging.getLogger().debug('Temporary file created. {0}'.format({'path' : filepath}))
        
        return (fd, filepath)
    
    @staticmethod
    @atexit.register
    def rmdir():
        
        registry = Registry.instance()
        
        tempdir = registry.get('tempdir')
        
        if tempdir != None:
            
            logging.getLogger().debug('Removing temporary directory. {0}'.format({'path' : tempdir}))
            
            shutil.rmtree(path = tempdir)
            
            logging.getLogger().debug('Removed temporary directory. {0}'.format({'path' : tempdir}))
            
            registry.remove('tempdir')
        