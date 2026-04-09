import logging
import aiofiles
import aiofiles.os
from .commonfs import write_new_version, ResultContext, expanduser


logger = logging.getLogger('cterasdk.filesystem')


async def write(directory, name, handle):
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
        await overwrite(tempfile, handle)
    return ctx.value


async def overwrite(p, handle):
    """
    Write, without validation.

    :param Path p: Path
    :param bytes handle: Handle
    """
    async with aiofiles.open(p, 'w+b') as fd:
        if isinstance(fd, bytes):
            await fd.write(handle)
        else:
            async for chunk in handle.a_iter_content(chunk_size=8192):
                await fd.write(chunk)
    return p.as_posix()


async def mkdir(p, parents=False, exist_ok=True):
    """
    Create a directory using aiofiles.

    :param str p: The path to create (string or Path object).
    :param bool,optional parents: Create a path, including all parent directories
    :param bool,optional exist_ok: Suppress error if directory exists
    :return: Path
    :rtype: str
    :raises FileExistsError: If ``exist_ok`` is ``False`` and directory exists
    """
    location = expanduser(p)

    if parents:
        await aiofiles.os.makedirs(location, exist_ok=exist_ok)
    else:
        await aiofiles.os.mkdir(location, exist_ok=exist_ok)
        
    return location.as_posix()
