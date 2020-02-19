from .registry import Registry

from ..exception import RenameException, LocalDirectoryNotFound

import logging

from pathlib import Path

import os

class FileSystem:

    __instance = None

    @staticmethod 
    def instance():

        if FileSystem.__instance == None:

            FileSystem()

        return FileSystem.__instance

    def __init__(self):

        if FileSystem.__instance != None:

            raise Exception("FileSystem is a singleton class.")

        else:
            
            FileSystem.__instance = self
    
    def expanduser(self, path):
        
        return os.path.expanduser(path)
    
    def exists(self, filepath):
        
        return os.path.exists(filepath)
    
    def rename(self, dirpath, src, dst):
        
        source = os.path.join(dirpath, src)
        
        if self.exists(source):
            
            destination = os.path.join(dirpath, dst)
                
            os.rename(source, destination)
            
            return (dirpath, dst)
            
        else:
            
            logging.getLogger().error('Could not rename temporary file. File not found. {0}'.format({'path' : dirpath, 'temp' : src}))
            
            raise RenameException(dirpath, src, dst)
            
    def save(self, dirpath, filename, handle):
        
        dirpath = os.path.expanduser(dirpath)
        
        if not self.exists(dirpath):
            
            raise LocalDirectoryNotFound(dirpath)
        
        tempfile = filename + '.Chopin3'
        
        filepath = os.path.join(dirpath, tempfile)
        
        self.write(filepath, handle)
        
        origin = filename
        
        version = 0
        
        while True:
            
            try:
        
                dirpath, filename = self.rename(dirpath, tempfile, filename)
            
                logging.getLogger().debug('Renamed temporary file. {0}'.format({'path' : dirpath, 'temp' : tempfile, 'name' : filename}))
            
                break
                
            except (FileExistsError, IsADirectoryError) as error:
        
                logging.getLogger().debug('File exists. {0}'.format({'path' : dirpath, 'name' : filename}))
        
                version = version + 1
                
                filename = self.version(origin, version)
        
        filepath = os.path.join(dirpath, filename)
        
        logging.getLogger().info('Saved. {0}'.format({'path' : filepath}))
        
        return filepath
                    
    def version(self, filename, version):
        
        idx = filename.rfind('.')
        
        extension = ''
                
        if idx > 0:
            
            name = filename[:idx]
            
            extension = filename[idx:]

        else:

            name = filename
            
        return (name + ' ' + '(' + str(version) + ')' + extension)
    
    def write(self, filepath, handle):
        
        sizeof = 8192
        
        f = None
        
        try:
        
            f = open(filepath, 'w+b')
            
            while True:
                
                buffer = handle.read(sizeof)
                
                if not buffer:
                    
                    break
                    
                f.write(buffer)
            
        except OSError as error:
            
            # TODO
            
            pass
        
        finally:
            
            if f != None:
                
                f.close()
                
                logging.getLogger().debug('Saved temporary file. {0}'.format({'path' : filepath}))
                
            if handle != None:
                
                handle.close()