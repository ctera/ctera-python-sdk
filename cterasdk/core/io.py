from ..clients.synchronous import clients
from ..objects.endpoints import EndpointBuilder


class IO:

    def __init__(self, core):
        async_session = self._generic._async_session
        self._folders = clients.Folders(EndpointBuilder.new(core.base, core.context, '/folders/folders'),
                                        async_session, core._authenticator)
        self._upload = clients.Upload(EndpointBuilder.new(core.base, core.context, '/upload/folders'), async_session, core._authenticator)
        self._webdav = clients.Dav(EndpointBuilder.new(core.base, core.context, '/webdav'), async_session, core._authenticator)
