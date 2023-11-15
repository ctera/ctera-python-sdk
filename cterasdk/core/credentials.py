import logging

from .types import UserAccount
from .base_command import BaseCommand


class Credentials(BaseCommand):
    """
    Portal Credential Management APIs

    :ivar cterasdk.core.credentials.S3 s3: Object holding the Portal S3 Credential Management APIs.
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.s3 = S3(self._portal)


class S3(BaseCommand):
    """S3 Credential Management APIs"""

    def _user_account(self, user_account=None):
        return user_account if user_account else UserAccount(self._portal.session().user.name)

    def all(self, user_account=None):
        """
        List Credentials

        :param cterasdk.core.types.UserAccount,optional user_account: User account
        """
        user_account = self._user_account(user_account)
        param = self._portal.users.get(user_account, ['uid']).uid
        logging.getLogger().info('Listing Credentials. %s', {'user': str(user_account)})
        return self._portal.execute('', 'getApiKeys', param)

    def create(self, user_account=None):
        """
        Create Credential

        :param cterasdk.core.types.UserAccount,optional user_account: User account
        """
        user_account = self._user_account(user_account)
        param = self._portal.users.get(user_account, ['uid']).uid
        logging.getLogger().info('Creating Credential. %s', {'type': 's3', 'user': str(user_account)})
        response = self._portal.execute('', 'createApiKey', param)
        logging.getLogger().info('Credetial created. %s', {'type': 's3', 'user': str(user_account)})
        return response

    def delete(self, access_key_id, user_account=None):
        """
        Delete Credential

        :param str access_key_id: Access Key ID
        :param cterasdk.core.types.UserAccount,optional user_account: User account
        """
        user_account = self._user_account(user_account)
        for key in self.all(user_account):
            if key.accessKey == access_key_id:
                logging.getLogger().info('Deleting Credential. %s', {'type': 's3'})
                response = self._portal.execute('', 'deleteApiKey', key.uid)
                logging.getLogger().info('Credetial deleted. %s', {'type': 's3'})
                return response
        logging.getLogger().warning('Could not find access key. %s', {'key': access_key_id})
        return None
