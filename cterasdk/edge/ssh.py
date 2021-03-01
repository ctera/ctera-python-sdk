import logging
from ..lib import FileSystem, CryptoServices
from ..common import Object
from .base_command import BaseCommand


class SSH(BaseCommand):
    """ Edge Filer SSH daemon APIs """

    def enable(self, public_key=None, public_key_file=None, exponent=65537, key_size=2048):
        """
        Enable the Edge Filer's SSH daemon

        :param str,optional public_key: A PEM-encoded public key in OpenSSH format.
         If neither a public key nor public key file were specified, an RSA key pair will be generated automatically.
         The PEM-encoded private key will be saved to the default Downloads directory
        :param str,optional public_key_file: A path to the public key file
        :param int,optional exponent: The public exponent of the new key, defaults to `65537`
        :param int,optional key_size: The length of the modulus in bits, defaults to `2048`
        """
        param = Object()

        if public_key is None:
            if public_key_file is not None:
                FileSystem.instance().get_local_file_info(public_key_file)
                public_key = open(public_key_file, 'r').read()
            else:
                public_key = CryptoServices.generate_and_save_key_pair(self._gateway.host(), exponent=exponent, key_size=key_size)

        param.publicKey = public_key

        logging.getLogger().info("Enabling SSH daemon.")
        self._gateway.execute('/config/device', 'startSSHD', param)
        logging.getLogger().info("SSH daemon enabled.")

    def disable(self):
        logging.getLogger().info("Disabling SSH daemon.")
        self._gateway.execute('/config/device', 'stopSSHD')
        logging.getLogger().info("SSH daemon disabled.")
