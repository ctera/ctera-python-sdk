import logging
from .exceptions import BlockInfo


def blocks(file, array):
    """
    Filter Blocks by Block Number.

    :param list[cterasdk.direct.types.File] file: File Object.
    :param list[cterasdk.direct.exceptions.BlockInfo] array: List of BlockInfo objects,
     or list of integers identifying the block position.
    :returns: List of Chunks.
    :rtype: list[cterasdk.direct.types.Chunk]
    """
    if array is not None:
        numbers = [block.number if isinstance(block, BlockInfo) else block for block in array]
        return [file.chunks[number - 1] for number in numbers]
    return file.chunks


def span(file, byte_range):
    """
    Filter Blocks by Byte Range.

    :param list[cterasdk.direct.types.File] file: File Object.
    :param list[cterasdk.direct.types.ByteRange] byte_range: Byte Range.
    :returns: List of Chunks.
    :rtype: list[cterasdk.direct.types.Chunk]
    """
    if validate_byte_range(file, byte_range):
        start, end = None, None
        for index, chunk in enumerate(file.chunks):
            if byte_range.start < chunk.offset + chunk.length:
                start = index
                break
        if not byte_range.eof:
            for index, chunk in enumerate(file.chunks):
                if byte_range.end < chunk.offset + chunk.length:
                    end = index + 1
                    break
        return file.chunks[start:end]
    return file.chunks


def validate_byte_range(file, byte_range):
    size = file.size
    if byte_range.start > size:
        logging.getLogger('cterasdk.direct').error('Byte range start %s is greater than the file size %s.', byte_range.start, size)
        return False
    if not byte_range.eof and byte_range.end >= size:
        logging.getLogger('cterasdk.direct').debug('Byte range end is greater than file size.')
        byte_range.eof = True
    return True
