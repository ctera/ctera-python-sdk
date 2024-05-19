from ..services import CTERA
from ..endpoints import EndpointBuilder
from ...clients.asynchronous import clients


class DirectIO(CTERA):

    async def __aenter__(self):
        return self
    
    def __init__(self, host, port=None, https=True, token=None):
        super().__init__(host, port, https, base=None)
        self._io = clients.AsyncJSON(EndpointBuilder.new(self.base, '/directio'), authenticator=self._authenticator)
        self.__token = token

    async def get(self, file_id, token=None):
        """
        Get file.

        :param int file_id: File ID
        """
        return await self._io.get(f'{file_id}', headers={'Authorization': f'Bearer {token if token else self.__token}'})

    def _authenticator(self, url):
        return True
    
    async def __aexit__(self, exc_type, exc, tb):
        await self._io.shutdown()