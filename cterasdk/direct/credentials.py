import os
import logging
from abc import abstractmethod


logger = logging.getLogger('cterasdk.direct')


class BaseCredentials:
    """Base Credentials for CTERA Direct IO"""

    @property
    def bearer(self):
        return f'Bearer {self._bearer()}'

    @abstractmethod
    def _bearer(self):
        raise NotImplementedError("Subclass must implemenet the '_bearer' method.")


class KeyPair(BaseCredentials):
    """Access and Secret Key Pair"""

    def __init__(self, access_key_id, secret_access_key):
        logger.debug('Initializing client using Key Pair.')
        self.access_key_id = access_key_id if access_key_id else os.getenv('cterasdk.io.direct.access_key_id')
        self.secret_access_key = secret_access_key if secret_access_key else os.getenv('cterasdk.io.direct.secret_access_key')

    def _bearer(self):
        return self.access_key_id


class Bearer(BaseCredentials):
    """Bearer Token"""

    def __init__(self, bearer):
        logger.debug('Initializing client using Bearer token.')
        self.bearer = bearer if bearer else os.getenv('cterasdk.io.direct.bearer')

    def _bearer(self):
        return self.bearer
