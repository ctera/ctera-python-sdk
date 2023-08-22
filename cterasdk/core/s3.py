import logging

from .base_command import BaseCommand


class S3Keys(BaseCommand):
    """
    External S3Keys Management APIs
    :ivar cterasdk.core.s3.S3Keys : Object holding the Portal S3 User Keys APIs
    """

    def get_keys(self, user):
        """
        Retrieve all User Access Keys

        :param str user: Retrieve the Access Keys for the User
        """
        param = self._portal.users.get(user, ['uid']).uid
        return self._portal.execute('', 'getApiKeys', param)

    def add_key(self, user):
        """
        Add User Access Key

        :param str user: Create Access Key for the User
        """
        param = self._portal.users.get(user, ['uid']).uid
        logging.getLogger().info('Creating s3 API Key for user. %s', {'user': str(user)})
        response = self._portal.execute('', 'createApiKey', param)
        logging.getLogger().info('Created s3 API Key for user. %s', {'user': str(user)})
        return response

    def delete_key(self, user, access_key):
        """
        Delete User Access Key

        :param str user: Retrieve Access Key uid for the User
        :param str access_key: Delete the Access Key
        """
        for current_key in self.get_keys(user):
            if access_key == current_key.accessKey:
                logging.getLogger().info('Deleting s3 API Key. %s', {'access_key': access_key})
                response = self._portal.execute('', 'deleteApiKey', current_key.uid)
                logging.getLogger().info('Deleted s3 API Key. %s', {'access_key': access_key})
                return response
        logging.getLogger().warning('Could not find access key.')
        return None
