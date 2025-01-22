import logging
import gzip
import snappy
from .exceptions import DirectIOError


def decompress(compressed_block):
    """
    Decompress a Block.

    :param bytes block: Compressed Block
    :returns: Decompressed Block
    :rtype: bytes
    """
    if compressed_block.startswith(b'\x1f\x8b'):  # Gzip Standard Declaration.
        try:
            return gzip.decompress(compressed_block)
        except gzip.BadGzipFile:
            logging.getLogger('cterasdk.direct').error('Failed to Decompress Block. Bad Gzip.')
            raise DirectIOError()

    try:
        return decompress_with_magic_header(compressed_block) \
            if compressed_block.startswith(b'\x82SNAPPY\x00') else snappy.uncompress(compressed_block)  # Snappy Magic
    except snappy.UncompressError:
        logging.getLogger('cterasdk.direct').error('Failed to Decompress Block.')
        raise DirectIOError()


def decompress_with_magic_header(compressed_block):
    """
    Decompress a Block.

    :param bytes block: Compressed Block
    :returns: Decompressed Block
    :rtype: bytes
    """
    logging.getLogger('cterasdk.direct').debug('Decompressing Block.')
    decompressed_block = bytearray()
    size_of_data = len(compressed_block)
    chunk_size, chunk_start = 4, 16
    while chunk_start < size_of_data:
        chunk_end = chunk_start + chunk_size + int.from_bytes(compressed_block[chunk_start:chunk_start + chunk_size], byteorder='big')
        chunk_start = chunk_start + chunk_size
        if chunk_end > size_of_data:
            break
        decompressed_block.extend(snappy.decompress(compressed_block[chunk_start:chunk_end]))
        chunk_start = chunk_end
    return decompressed_block
