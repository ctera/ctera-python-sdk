import base64
import logging
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import UnsupportedAlgorithm
from ..common.utils import utf8_decode
from .exceptions import DirectIOError


def decrypt_key(wrapped_key, secret):
    try:
        logging.getLogger('cterasdk.direct').debug('Decoding Secret.')
        decoded_secret = base64.b64decode(secret)
        decoded_secret = decoded_secret[:32] + b'\0' * (32 - len(decoded_secret))
        decryptor = Cipher(algorithms.AES(decoded_secret), modes.ECB()).decryptor()
        logging.getLogger('cterasdk.direct').debug('Decrypting Encryption Key.')
        decrypted_wrapped_key = utf8_decode(decryptor.update(base64.b64decode(wrapped_key)))
        decrypted_key = ''.join(c for c in decrypted_wrapped_key if c.isprintable())[1:-1]
        return base64.b64decode(decrypted_key)
    except (AssertionError, ValueError, binascii.Error) as error:
        logging.getLogger('cterasdk.direct').error('Could not decrypt secret key. %s', error)
    raise DirectIOError()


def decrypt_block(block, encryption_key):
    try:
        initialization_vector = block[1:17]
        encrypted_data = block[17:]
        logging.getLogger('cterasdk.direct').debug('Decrypting Block.')
        decryptor = Cipher(algorithms.AES(encryption_key), modes.CBC(initialization_vector)).decryptor()
        return decryptor.update(encrypted_data)
    except ValueError as error:
        logging.getLogger('cterasdk.direct').error('Failed to decrypt block. Key error. %s', error)
    except UnsupportedAlgorithm as error:
        logging.getLogger('cterasdk.direct').error('Failed to decrypt block. Unsupported algorithm. %s', error)
    raise DirectIOError()
