from .path import CTERAPath

from ..base_command import BaseCommand
from . import ls, dl, directory, rename, rm, recover, mv, cp, ln


class FileBrowser(BaseCommand):

    def __init__(self, portal, base_path):
        super().__init__(portal)
        self._base_path = base_path

    def ls(self, path):
        return ls.ls(self._portal, self.mkpath(path))

    def walk(self, path):
        paths = [self.mkpath(path)]

        while len(paths) > 0:
            path = paths.pop(0)
            items = ls.ls(self._portal, path)
            for item in items:
                if item.isFolder:
                    paths.append(self.mkpath(item))
                yield item

    def download(self, path):
        path = self.mkpath(path)
        dl.download(self._portal, path, path.name())

    def mkdir(self, path, recurse=False):
        directory.mkdir(self._portal, self.mkpath(path), recurse)

    def rename(self, path, name):
        return rename.rename(self._portal, self.mkpath(path), name)

    def delete(self, path):
        return rm.delete(self._portal, self.mkpath(path))

    def delete_multi(self, *args):
        return rm.delete_multi(self._portal, *self.mkpath(list(args)))

    def undelete(self, path):
        return recover.undelete(self._portal, self.mkpath(path))

    def undelete_multi(self, *args):
        return recover.undelete_multi(self._portal, *self.mkpath(list(args)))

    def move(self, src, dest):
        return mv.move(self._portal, self.mkpath(src), self.mkpath(dest))

    def move_multi(self, src, dest):
        return mv.move_multi(self._portal, self.mkpath(src), self.mkpath(dest))

    def copy(self, src, dest):
        return cp.copy(self._portal, self.mkpath(src), self.mkpath(dest))

    def copy_multi(self, src, dest):
        return cp.copy_multi(self._portal, self.mkpath(src), self.mkpath(dest))

    def mklink(self, path, access='RO', expire_in=30):
        return ln.mklink(self._portal, self.mkpath(path), access, expire_in)

    def mkpath(self, array):
        if isinstance(array, list):
            return [CTERAPath(item, self._base_path) for item in array]
        return CTERAPath(array, self._base_path)
