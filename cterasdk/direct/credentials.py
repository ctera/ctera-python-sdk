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
