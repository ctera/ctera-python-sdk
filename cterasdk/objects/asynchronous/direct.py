from collections import namedtuple

from ..services import CTERA
from ..endpoints import EndpointBuilder
from ...clients.asynchronous import clients


from ...direct import io


Credential = namedtuple('Credential', ('access_key_id', 'secret_access_key'))
Credential.__doc__ = 'Tuple holding the access and secret keys to access objects using DirectIO'
Credential.access_key_id.__doc__ = 'Access key'
Credential.secret_access_key.__doc__ = 'Secret Key'


class DirectIO(CTERA):

    async def __aenter__(self):
        return self
    
    def __init__(self, host, port=None, https=True, credential=None):
        super().__init__(host, port, https, base=None)
        self._direct = clients.DirectIO(EndpointBuilder.new(self.base, '/directio'), authenticator=self._authenticator)
        self.__credential = credential

    async def get(self, file_id, credential=None):
        """
        Get file.

        :param int file_id: File ID
        :param cterasdk.objects.asynchronous.direct.Credential credential: Credential
        """
        return await io.get(self._direct, file_id, credential if credential else self.__credential)

    def _authenticator(self, url):
        return True
    
    async def __aexit__(self, exc_type, exc, tb):
        await self._direct.shutdown()
