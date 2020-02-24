from pathlib import PurePosixPath
from urllib.parse import quote, unquote
import re

from ...exception import InputError
from ...common import Object


class CTERAPath:

    def __init__(self, item, basepath):
        if isinstance(item, str):
            self.basepath = PurePosixPath(basepath)
            self.relativepath = PurePosixPath(item)
        elif isinstance(item, Object) and hasattr(item, '_classname') and item._classname == 'ResourceInfo':
            href = unquote(item.href)
            match = re.search('^/(ServicesPortal|Users)/webdav', href)
            start, end = match.span()
            self.basepath = PurePosixPath(href[start: end])
            self.relativepath = PurePosixPath(href[end + 1:])
        else:
            raise InputError('Invalid path', item, 'comma separated str path segments, or a ResourceInfo object')

        if self.relativepath.root == '/' or self.basepath.joinpath(self.relativepath) == self.relativepath:
            raise InputError(
                'You must specify a relative path. Omit leading / characters',
                str(self.relativepath),
                re.sub(r'^/*', '', str(self.relativepath))
            )

    def name(self):
        return self.relativepath.name

    def parent(self):
        return CTERAPath(str(self.relativepath.parent), str(self.basepath))

    def fullpath(self):
        return str(self.basepath.joinpath(self.relativepath))

    def encoded_fullpath(self):
        return quote(self.fullpath())

    def encoded_parent(self):
        return quote(str(self.parent()))

    def joinpath(self, path):
        return CTERAPath(str(self.relativepath.joinpath(path)), str(self.basepath))

    def parts(self):
        return self.relativepath.parts

    def __str__(self):
        return self.fullpath()
