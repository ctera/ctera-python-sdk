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


def create_authorization_header(credentials):
    """
    Create Authorization Header.

    :param cterasdk.direct.credentials.BaseCredentials credentials: Credentials
    :returns: Authorization header as a dictionary.
    :rtype: dict
    """
    authorization_header = None

    if isinstance(credentials, Bearer):
        logger.debug('Initializing client using bearer token')
        authorization_header = f'Bearer {credentials.bearer}'

    elif isinstance(credentials, KeyPair):
        logger.debug('Initializing client using key pair.')
        authorization_header = f'Bearer {credentials.access_key_id}'

    return {'Authorization': authorization_header}
