import logging
from .commonfs import write_new_version, ResultContext


logger = logging.getLogger('cterasdk.filesystem')


def write(directory, name, handle):
    """
    Write bytes to disk.

    :param str directory: Directory
    :param str name: Name
    :param bytes handle: Handle
    :returns: Path
    :rtype: str
    """
    ctx = ResultContext()
    with write_new_version(directory, name, ctx=ctx) as tempfile:
        overwrite(tempfile, handle)
    return ctx.value


def overwrite(p, handle):
    """
    Write, without validation.

    :param Path p: Path
    :param bytes handle: Handle
    """
    with open(p, 'w+b') as fd:
        if isinstance(handle, bytes):
            fd.write(handle)
        else:
            for chunk in handle.iter_content(chunk_size=8192):
                fd.write(chunk)
        logger.debug('Wrote: %s', p.as_posix())
    return p.as_posix()
