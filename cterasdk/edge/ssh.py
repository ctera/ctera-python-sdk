import logging
from ..lib import CryptoServices
from ..lib.storage import commonfs
from ..common import Object
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


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
                commonfs.properties(public_key_file)
                with open(public_key_file, 'r', encoding='utf-8') as f:
                    public_key = f.read()
            else:
                public_key = CryptoServices.generate_and_save_key_pair(self._edge.host(), exponent=exponent, key_size=key_size)

        param.publicKey = public_key

        logger.info("Enabling SSH daemon.")
        self._edge.api.execute('/config/device', 'startSSHD', param)
        logger.info("SSH daemon enabled.")

    def disable(self):
        logger.info("Disabling SSH daemon.")
        self._edge.api.execute('/config/device', 'stopSSHD')
        logger.info("SSH daemon disabled.")
