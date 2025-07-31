import logging


logger = logging.getLogger('cterasdk.direct')


class BaseCredentials:
    """Base Credentials for CTERA Direct IO"""


class KeyPair(BaseCredentials):
    """Access and Secret Key Pair"""

    def __init__(self, access_key_id, secret_access_key):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key


class Bearer(BaseCredentials):
    """Bearer Token"""

    def __init__(self, bearer):
        self.bearer = bearer


def create_bearer_token(credentials):
    """
    Create Authorization Header.

    :param cterasdk.direct.credentials.BaseCredentials credentials: Credentials
    :returns: Authorization header as a dictionary.
    :rtype: dict
    """
    token = None

    if isinstance(credentials, Bearer):
        logger.debug('Initializing client using Bearer token')
        token = f'Bearer {credentials.bearer}'

    elif isinstance(credentials, KeyPair):
        logger.debug('Initializing client using Key Pair.')
        token = f'Bearer {credentials.access_key_id}'

    return token
