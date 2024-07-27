import logging
from ..exceptions import BlockError


def blocks(file, blocks):
    """
    Filter Blocks by Block Number.

    :param list[cterasdk.direct.types.File] file: File Object.
    :param list[cterasdk.direct.types.BlockError] blocks: List of BlockError objects or integers.
    :returns: List of Chunks.
    :rtype: list[cterasdk.direct.types.Chunk]
    """
    if blocks is not None:
        chunks = [block.number if isinstance(block, BlockError) else block for block in blocks]
        return [file.chunks[number - 1] for number in chunks]
    return file.chunks


def bytes(file, byte_range):
    """
    Filter Blocks by Byte Range.

    :param list[cterasdk.direct.types.File] file: File Object.
    :param list[cterasdk.direct.types.ByteRange] byte_range: Byte Range.
    :returns: List of Chunks.
    :rtype: list[cterasdk.direct.types.Chunk]
    """
    if validate_byte_range(file, byte_range):
        start, end = None, None
        for i in range(0, len(file.chunks)):
            chunk = file.chunks[i]
            if byte_range.start < chunk.offset + chunk.length:
                start = i
                break
        if not byte_range.eof:
            for i in range(0, len(file.chunks)):
                chunk = file.chunks[i]
                if byte_range.end < chunk.offset + chunk.length:
                    end = i + 1
                    break
        return file.chunks[start:end]
    return file.chunks


def validate_byte_range(file, byte_range):
    size = file.size
    if byte_range.start > size:
        logging.getLogger('cterasdk.direct').error(f'Byte range start {byte_range.start} is greater than the file size {size}.')
        return False
    if not byte_range.eof and byte_range.end >= size:
        logging.getLogger('cterasdk.direct').debug('Byte range end is greater than file size.')
        byte_range.eof = True
    return True
    