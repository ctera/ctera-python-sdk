import logging
import snappy
from .exceptions import DirectIOError


def decompress(compressed_block):
    """
    Decompress a Block.

    :param bytes block: Compressed Block
    :returns: Decompressed Block
    :rtype: bytes
    """
    return decompress_with_magic_header(compressed_block) \
        if compressed_block.startswith(b'\x82SNAPPY\x00') else decompress_without_magic_header(compressed_block)


def decompress_with_magic_header(compressed_block):
    """
    Decompress a Block.

    :param bytes block: Compressed Block
    :returns: Decompressed Block
    :rtype: bytes
    """
    try:
        logging.getLogger('cterasdk.direct').debug('Decompressing Block.')
        decompressed_block = bytearray()
        size_of_data = len(compressed_block)
        chunk_size, chunk_start = 4, 16
        while chunk_start < size_of_data:
            chunk_end = chunk_start + chunk_size + int.from_bytes(compressed_block[chunk_start:chunk_start + chunk_size])
            chunk_start = chunk_start + chunk_size
            if chunk_end > size_of_data:
                break
            decompressed_block.extend(snappy.decompress(compressed_block[chunk_start:chunk_end]))
            chunk_start = chunk_end
        return decompressed_block
    except snappy.UncompressError:
        raise DirectIOError()


def decompress_without_magic_header(compressed_block):
    """
    Decompress a Block.

    :param bytes compressed_block: Compressed Block
    :returns: Decompressed Block
    :rtype: bytes
    """
    return snappy.uncompress(compressed_block[:compressed_block.rfind(b'EOF') + 3])
