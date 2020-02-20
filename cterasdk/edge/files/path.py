from pathlib import PurePosixPath
import re
from urllib.parse import quote

from ...exception import InputError


class CTERAPath:

    def __init__(self, relativepath, basepath):
        self.basepath = PurePosixPath(basepath)
        self.relativepath = PurePosixPath(relativepath)
        if self.basepath.joinpath(self.relativepath) == self.relativepath:
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
