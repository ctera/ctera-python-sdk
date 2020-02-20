from ...common import Object


class SrcDstParam(Object):

    __instance = None

    @staticmethod
    def instance(src, dest=None):
        SrcDstParam(src, dest)
        return SrcDstParam.__instance

    def __init__(self, src, dest=None):
        self._classname = self.__class__.__name__
        self.src = src
        self.dest = dest
        SrcDstParam.__instance = self


class ActionResourcesParam(Object):

    __instance = None

    @staticmethod
    def instance():
        ActionResourcesParam()
        return ActionResourcesParam.__instance

    def __init__(self):
        self._classname = self.__class__.__name__
        self.urls = []
        ActionResourcesParam.__instance = self

    def add(self, param):
        self.urls.append(param)


class CreateShareParam(Object):

    __instance = None

    @staticmethod
    def instance(path, access, expire_on):
        CreateShareParam(path, access, expire_on)
        return CreateShareParam.__instance

    def __init__(self, path, access, expire_on):
        self._classname = self.__class__.__name__
        self.url = path
        self.share = Object()
        self.share._classname = 'ShareConfig'
        self.share.accessMode = access
        self.share.protectionLevel = 'publicLink'
        self.share.expiration = expire_on
        self.share.invitee = Object()
        self.share.invitee._classname = 'Collaborator'
        self.share.invitee.type = 'external'
        CreateShareParam.__instance = self
