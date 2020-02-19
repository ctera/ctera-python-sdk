from .path import CTERAPath

from . import ls, dl, directory, rename, rm, recover, mv, cp, ln

#from . import List, Download, Directory, Rename, Delete, Recover, Move, Copy, Link

class FileBrowser:

    def __init__(self, Portal):
        
        self._CTERAHost = Portal
        
    def ls(self, path):
        
        return ls.ls(self._CTERAHost, self.mkpath(path))
    
    def walk(self, path):
        
        paths = [self.mkpath(path)]
        
        while len(paths) > 0:
            
            path = paths.pop(0)
            
            items = ls.ls(self._CTERAHost, path)
            
            for item in items:
                
                if item.isFolder:
                    
                    paths.append(self.mkpath(item))
                    
                yield item       
        
    def download(self, path):
        
        path = self.mkpath(path)
        
        dl.download(self._CTERAHost, path, path.name())

    def mkdir(self, path, recurse = False):
    
        directory.mkdir(self._CTERAHost, self.mkpath(path), recurse) 
        
    def rename(self, path, name):
        
        return rename.rename(self._CTERAHost, self.mkpath(path), name)
    
    def delete(self, path):
        
        return rm.delete(self._CTERAHost, self.mkpath(path))
    
    def delete_multi(self, *args):
        
        return rm.delete_multi(self._CTERAHost, *self.mkpath(list(args)))
    
    def undelete(self, path):
        
        return recover.undelete(self._CTERAHost, self.mkpath(path))
    
    def undelete_multi(self, *args):
        
        return recover.undelete_multi(self._CTERAHost, *self.mkpath(list(args)))
    
    def move(self, src, dest):
        
        return mv.move(self._CTERAHost, self.mkpath(src), self.mkpath(dest))
    
    def move_multi(self, src, dest):
        
        return mv.move_multi(self._CTERAHost, self.mkpath(src), self.mkpath(dest))
    
    def copy(self, src, dest):
        
        return cp.copy(self._CTERAHost, self.mkpath(src), self.mkpath(dest))
    
    def copy_multi(self, src, dest):
        
        return cp.copy_multi(self._CTERAHost, self.mkpath(src), self.mkpath(dest))
    
    def mklink(self, path, access = 'RO', expire_in = 30):
        
        return ln.mklink(self._CTERAHost, self.mkpath(path), access, expire_in)
    
    def mkpath(self, array):
        
        basepath = self._files()
        
        if isinstance(array, list):
            
            return [CTERAPath(item, basepath) for item in array]
    
        else:
            
            return CTERAPath(array, basepath)
    
    def _files(self):
        
        return self._CTERAHost._files()
        
        
