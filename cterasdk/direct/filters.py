import logging


logger = logging.getLogger('cterasdk.direct')


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
        logger.error('Byte range start %s is greater than the file size %s.', byte_range.start, size)
        return False
    if not byte_range.eof and byte_range.end >= size:
        logger.debug('Byte range end is greater than file size.')
        byte_range.eof = True
    return True
