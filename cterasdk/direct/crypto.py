import base64
import logging
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import UnsupportedAlgorithm
from ..common.utils import utf8_decode
from ..exceptions.direct import DirectIOError


logger = logging.getLogger('cterasdk.direct')


def decrypt_key(wrapped_key, secret):
    try:
        logger.debug('Decoding Secret.')
        decoded_secret = base64.b64decode(secret)
        decoded_secret = decoded_secret[:32] + b'\0' * (32 - len(decoded_secret))
        decryptor = Cipher(algorithms.AES(decoded_secret), modes.ECB()).decryptor()
        logger.debug('Decrypting Encryption Key.')
        decrypted_wrapped_key = utf8_decode(decryptor.update(base64.b64decode(wrapped_key)))
        decrypted_key = ''.join(c for c in decrypted_wrapped_key if c.isprintable())[1:-1]
        return base64.b64decode(decrypted_key)
    except (AssertionError, ValueError, binascii.Error) as error:
        logger.error('Could not decrypt secret key. %s', error)
    raise DirectIOError()


def decrypt_block(block, encryption_key):
    try:
        initialization_vector = block[1:17]
        encrypted_data = block[17:]
        logger.debug('Decrypting Block.')
        decryptor = Cipher(algorithms.AES(encryption_key), modes.CBC(initialization_vector)).decryptor()
        decrypted_data = decryptor.update(encrypted_data)
        return decrypted_data[:-decrypted_data[-1]]  # Remove CBC Padding
    except ValueError as error:
        logger.error('Failed to decrypt block. Key error. %s', error)
    except UnsupportedAlgorithm as error:
        logger.error('Failed to decrypt block. Unsupported algorithm. %s', error)
    raise DirectIOError()
