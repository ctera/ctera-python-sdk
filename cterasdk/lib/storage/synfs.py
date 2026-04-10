import logging
from .commonfs import write_new_version, ResultContext, expanduser


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


def mkdir(p, parents=False, exist_ok=True):
    """
    Create a directory.

    :param str p: The path to create (string or Path object).
    :param bool,optional parents: Create a path, including all parent directories
    :param bool,optional exist_ok: Suppress error if directory exists
    :return: Path
    :rtype: str
    :raises FileExistsError: If ``exist_ok`` is ``False`` and directory exists
    """
    location = expanduser(p)
    location.mkdir(parents=parents, exist_ok=exist_ok)
    return location.as_posix()
