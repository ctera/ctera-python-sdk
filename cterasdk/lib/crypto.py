import re
import os
import logging
import functools

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption, load_pem_private_key

import cterasdk.settings
from ..exceptions import CTERAException
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

        logging.getLogger('cterasdk.crypto').info('Saving private key.')
        path = filesystem.save(dirpath, f'{key_filename}.pem', self.private_key)
        os.chmod(path, 0o600)
        logging.getLogger('cterasdk.crypto').info('Saved private key. %s', {'filepath': path, 'format': 'PEM'})

        logging.getLogger('cterasdk.crypto').info('Saving public key.')
        path = filesystem.save(dirpath, f'{key_filename}.pub', self.public_key)
        logging.getLogger('cterasdk.crypto').info('Saved public key. %s', {'filepath': path, 'format': 'OpenSSH'})


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
            dirpath = cterasdk.settings.downloads.location
        key_pair.save(dirpath, key_filename)
        return key_pair.public_key.decode('utf-8')


def create_certificate_chain(*certificates):
    return sorted(certificates, key=functools.cmp_to_key(compare_certificates))


def compare_certificates(a, b):
    if a.subject == b.issuer:
        return 1
    if b.subject == a.issuer:
        return -1
    return 0


class PrivateKey:

    def __init__(self, private_key):
        self.private_key = private_key

    @property
    def pem_data(self):
        return self.private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())

    @staticmethod
    def from_file(path, password=None):
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
        return PrivateKey.from_string(data, password)

    @staticmethod
    def from_string(data, password=None):
        return PrivateKey.from_bytes(data.encode('utf-8'), password)

    @staticmethod
    def from_bytes(data, password=None):
        return PrivateKey(load_pem_private_key(data, password))

    @staticmethod
    def load_private_key(key, password=None):
        try:
            if isinstance(key, bytes):
                return PrivateKey.from_bytes(key, password)

            if FileSystem.instance().exists(key):
                return PrivateKey.from_file(key, password)
            return PrivateKey.from_string(key, password)
        except ValueError as e:
            logging.getLogger('cterasdk.crypto').error('Failed loading private key.')
            raise CTERAException('Failed loading private key', e, reason=str(e))


class X509Certificate:

    def __init__(self, certificate):
        self.certificate = certificate

    @property
    def sha1_fingerprint(self):
        hexstr = self.certificate.fingerprint(hashes.SHA1()).hex()
        return ':'.join([a + b for a, b in zip(hexstr[::2], hexstr[1::2])])

    @property
    def issuer(self):
        return X509Certificate._parse_common_name(self.certificate.issuer.rdns[-1].rfc4514_string())

    @property
    def subject(self):
        return X509Certificate._parse_common_name(self.certificate.subject.rdns[-1].rfc4514_string())

    @property
    def is_root(self):
        return self.issuer == self.subject

    @property
    def pem_data(self):
        return self.certificate.public_bytes(Encoding.PEM)

    @staticmethod
    def _parse_common_name(common_name):
        match = re.search(r'(?<=CN=).+$', common_name)
        return match.group(0) if match else None

    @staticmethod
    def from_file(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
        return X509Certificate.from_string(data)

    @staticmethod
    def from_string(data):
        return X509Certificate.from_bytes(data.encode('utf-8'))

    @staticmethod
    def from_bytes(data):
        return X509Certificate(x509.load_pem_x509_certificate(data))

    @staticmethod
    def load_certificate(cert):
        try:
            if isinstance(cert, bytes):
                return X509Certificate.from_bytes(cert)

            if FileSystem.instance().exists(cert):
                return X509Certificate.from_file(cert)
            return X509Certificate.from_string(cert)
        except ValueError as e:
            logging.getLogger('cterasdk.crypto').error('Failed loading certificate.')
            raise CTERAException('Failed loading certificate', e, reason=str(e))

    def __str__(self):
        return str(
            dict(
                issued_to=self.subject,
                issued_by=self.issuer
            )
        )
