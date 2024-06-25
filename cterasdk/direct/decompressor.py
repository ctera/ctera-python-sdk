import snappy
import struct
import logging


def decompress(block) -> bytes:
    """
    Public method to decompress the data.

    Returns:
        bytes: The decompressed data.
    """
    return __decompress_snappy_with_magic(block) if block[1:7] == b'SNAPPY' else __decompress_snappy_without_magic(block)



def _chunks(compressed_block):
    """
    Get Chunks Range if Compression Performed Using Chunks.

    :param bytes block: Compressed Block
    :returns: List of Slices
    :rtype: list[(int, int)]
    """
    chunks = []
    size_of_data = len(compressed_block)
    chunk_size, chunk_start = 4, 16, None
    while chunk_start < size_of_data:
        chunk_end = chunk_start + chunk_size + int.from_bytes(compressed_block[chunk_start:chunk_start + chunk_size])
        chunk_start = chunk_start + chunk_size
        if chunk_end > size_of_data:
            break
        chunks.append((chunk_start, chunk_end))
        chunk_start = chunk_end
    return chunks


def _decompress_chunks(compressed_block):
    """
    Decompress a Block.

    :param bytes block: Compressed Block
    :returns: Decompressed Block
    :rtype: bytes
    """
    decompressed_block = bytes()
    chunks = _chunks(compressed_block)
    for chunk_start, chunk_end in chunks:
        decompressed_block += snappy.decompress(compressed_block[chunk_start:chunk_end])
    return decompressed_block


def __decompress_snappy_with_magic(block) -> bytes:
    """
    Method to decompress Snappy compressed data with a magic header.

    Returns:
        bytes: The decompressed data.
    """
    index = 16  # Skip headers
    full_data = bytes()
    while index+4 < len(block):
        try:
            # Unpack the chunk size (4 bytes, big-endian)
            chunk_size = struct.unpack('>i', block[index:index + 4])[0]

            # Check if the chunk size is within valid bounds
            if chunk_size + index > len(block) or chunk_size + index < 0:
                break
        except struct.error:
            logging.getLogger('cterasdk.direct').error("Error unpacking data")
        except BaseException as e:
            logging.getLogger('cterasdk.direct').error(f"Unknown error: {e}")
            break
        index += 4
        # Unpack the chunk data and decompress using Snappy
        chunk_data = struct.unpack(str(chunk_size) + 's', block[index:index + chunk_size])[0]
        index += chunk_size
        full_data += snappy.decompress(chunk_data)
    return full_data


def __decompress_snappy_without_magic(block) -> bytes:
    """
    Private method to decompress Snappy compressed data without a magic header.

    Returns:
        bytes: The decompressed data.
    """
    byte_to_find = b'\xff'
    last_byte = block.rfind(byte_to_find)
    for i in range(last_byte, len(block)):
        # Check for valid compressed data using Snappy
        if snappy.isValidCompressed(block[0:i]):
            last_byte = i
    return snappy.decompress(block[0:last_byte])
