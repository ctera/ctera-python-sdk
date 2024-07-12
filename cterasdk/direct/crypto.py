import base64
import logging
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import UnsupportedAlgorithm
from ..common.utils import utf8_decode
from ..exceptions import CTERAException


def decrypt_key(wrapped_key, secret):
    try:
        decoded_secret = base64.b64decode(secret)
        decoded_secret = decoded_secret[:32] + b'\0' * (32 - len(decoded_secret))
        decryptor = Cipher(algorithms.AES(decoded_secret), modes.ECB()).decryptor()
        decrypted_wrapped_key = utf8_decode(decryptor.update(base64.b64decode(wrapped_key)))
        decrypted_key = ''.join(c for c in decrypted_wrapped_key if c.isprintable())[1:-1]
        return base64.b64decode(decrypted_key)
    except (AssertionError, ValueError, binascii.Error) as error:
        logging.getLogger('cterasdk.direct').error(f'Could not decrypt secret key. {error}')
    raise CTERAException('Could not decrypt secret key.')


def decrypt_block(block, encryption_key):
    try:
        initialization_vector = block[1:17]
        encrypted_data = block[17:]
        decryptor = Cipher(algorithms.AES(encryption_key), modes.CBC(initialization_vector)).decryptor()
        return decryptor.update(encrypted_data)
    except ValueError as error:
        logging.getLogger('cterasdk.direct').error(f'Could not decrypt block. Key error. {error}')
    except UnsupportedAlgorithm as error:
        logging.getLogger('cterasdk.direct').error(f'Could not decrypt block. Unsupported algorithm. {error}')
    raise CTERAException('Could not decrypt block.')
