import logging
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

from .. import config
from .filesystem import FileSystem


class RSAKeyPair:

    def __init__(self, private_key, public_key):
        self._private_key = private_key
        self._public_key = public_key

    @property
    def public_key(self):
        return self._public_key.public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)

    @property
    def private_key(self):
        return self._private_key.private_bytes(Encoding.PEM, PrivateFormat.OpenSSH, NoEncryption())

    def save(self, dirpath, key_filename):
        filesystem = FileSystem.instance()

        logging.getLogger().info('Saving private key.')
        path = filesystem.save(dirpath, '{}.pem'.format(key_filename), self.private_key)
        logging.getLogger().info('Saved private key. %s', {'filepath': path, 'format': 'PEM'})

        logging.getLogger().info('Saving public key.')
        path = filesystem.save(dirpath, '{}.pub'.format(key_filename), self.public_key)
        logging.getLogger().info('Saved public key. %s', {'filepath': path, 'format': 'OpenSSH'})


class CryptoServices:

    @staticmethod
    def generate_rsa_key_pair(exponent=65537, key_size=2048):
        private_key = rsa.generate_private_key(public_exponent=exponent, key_size=key_size)
        public_key = private_key.public_key()
        return RSAKeyPair(private_key, public_key)

    @staticmethod
    def generate_and_save_key_pair(key_filename, exponent=65537, key_size=2048, dirpath=None):
        key_pair = CryptoServices.generate_rsa_key_pair(exponent, key_size)
        if not dirpath:
            dirpath = config.filesystem['dl']
        key_pair.save(dirpath, key_filename)
        return key_pair.public_key.decode('utf-8')
