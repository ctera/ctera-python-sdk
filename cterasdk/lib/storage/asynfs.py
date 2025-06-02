import logging
import aiofiles
from .commonfs import write_new_version, ResultContext


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
    with write_new_version(directory, name) as tempfile:
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
