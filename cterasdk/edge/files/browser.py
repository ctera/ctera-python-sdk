from .path import CTERAPath

from . import dl, mkdir, rm

class FileBrowser:

    def __init__(self, Gateway):
        
        self._CTERAHost = Gateway
        
    def ls(self, path):
        
        return
        
    def download(self, path):
        
        return dl.download(self._CTERAHost, self.mkpath(path))

    def mkdir(self, path, recurse = False):
    
        return mkdir.mkdir(self._CTERAHost, self.mkpath(path), recurse)
    
    def delete(self, path):
        
        return rm.delete(self._CTERAHost, self.mkpath(path))
    
    def mkpath(self, path):
        
        return CTERAPath(path, '/')
    
    def _files(self):
        
        return self._CTERAHost._files()
        
        
