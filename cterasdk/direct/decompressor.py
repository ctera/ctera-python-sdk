import snappy


def _chunks(compressed_block):
    """
    Get Chunks Range if Compression Performed Using Chunks.

    :param bytes block: Compressed Block
    :returns: List of Slices
    :rtype: list[(int, int)]
    """
    chunks = []
    size_of_data = len(compressed_block)
    chunk_size, chunk_start = 4, 16
    while chunk_start < size_of_data:
        chunk_end = chunk_start + chunk_size + int.from_bytes(compressed_block[chunk_start:chunk_start + chunk_size])
        chunk_start = chunk_start + chunk_size
        if chunk_end > size_of_data:
            break
        chunks.append((chunk_start, chunk_end))
        chunk_start = chunk_end
    return chunks


def decompress(compressed_block):
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