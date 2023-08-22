import logging

from .base_command import BaseCommand
from ..common import Object, utf8_decode, union
from . import query


class S3Keys(BaseCommand):

    def get_keys(self, user):
        param = self._portal.users.get(user, ['uid']).uid
        return self._portal.execute('', 'getApiKeys', param)

    def add_key(self, user):
        param = self._portal.users.get(user, ['uid']).uid
        logging.getLogger().info('Creating s3 API Key for user. %s', {'user': str(user)})
        response = self._portal.execute('', 'createApiKey', param)
        logging.getLogger().info('Created s3 API Key for user. %s', {'user': str(user)})
        return response

    def delete_key(self, user, access_key):
        for current_key in self.get_keys(user):
            if access_key == current_key.accessKey:
                logging.getLogger().info('Deleting s3 API Key. %s', {'access_key': access_key})
                response = self._portal.execute('', 'deleteApiKey', current_key.uid)
                logging.getLogger().info('Deleted s3 API Key. %s', {'access_key': access_key})
                return response
        logging.getLogger().warning('Could not find access key.')
        return None
