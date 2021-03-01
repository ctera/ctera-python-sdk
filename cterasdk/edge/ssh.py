import logging
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
from .. import config
from ..lib import FileSystem
from ..common import Object
from .base_command import BaseCommand


class SSH(BaseCommand):
    """ Edge Filer SSH daemon APIs """

    def enable(self, public_key=None, exponent=65537, key_size=2048):
        """
        Enable the Edge Filer's SSH daemon

        :param str,optional public_key: A PEM-encoded public key in OpenSSH format.
         If not specified, an RSA key pair will be generated automatically.
         The PEM-encoded private key will be saved to the default Downloads directory
        :param int,optional exponent: The public exponent of the new key, defaults to `65537`
        :param int,optional key_size: The length of the modulus in bits, defaults to `2048`
        """
        param = Object()

        private_key = None
        if not public_key:
            private_key = rsa.generate_private_key(public_exponent=exponent, key_size=key_size)
            public_key = private_key.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)

        param.publicKey = public_key.decode('utf-8')

        if private_key:
            dirpath = config.filesystem['dl']
            logging.getLogger().info('Saving private key.')
            filepath = FileSystem.instance().save(dirpath, '{}.pem'.format(self._gateway.host()),
                                                  private_key.private_bytes(Encoding.PEM, PrivateFormat.OpenSSH, NoEncryption()))
            logging.getLogger().info('Saved private key. %s', {'filepath': filepath, 'format': 'PEM'})

            logging.getLogger().info('Saving public key.')
            filepath = FileSystem.instance().save(dirpath, '{}.pub'.format(self._gateway.host()), public_key)
            logging.getLogger().info('Saved public key. %s', {'filepath': filepath, 'format': 'OpenSSH'})

        logging.getLogger().info("Enabling SSH daemon.")
        self._gateway.execute('/config/device', 'startSSHD', param)
        logging.getLogger().info("SSH daemon enabled.")

    def disable(self):
        logging.getLogger().info("Disabling SSH daemon.")
        self._gateway.execute('/config/device', 'stopSSHD')
        logging.getLogger().info("SSH daemon disabled.")
