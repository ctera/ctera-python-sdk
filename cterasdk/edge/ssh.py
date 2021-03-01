import logging
from .. import config
from ..lib import CryptoServices
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

        if not public_key:
            key_pair = CryptoServices.generate_rsa_key_pair(exponent, key_size)
            public_key = key_pair.public_key
            key_pair.save(config.filesystem['dl'], self._gateway.host())

        param.publicKey = public_key.decode('utf-8')

        logging.getLogger().info("Enabling SSH daemon.")
        self._gateway.execute('/config/device', 'startSSHD', param)
        logging.getLogger().info("SSH daemon enabled.")

    def disable(self):
        logging.getLogger().info("Disabling SSH daemon.")
        self._gateway.execute('/config/device', 'stopSSHD')
        logging.getLogger().info("SSH daemon disabled.")
