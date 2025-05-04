import logging
import aiofiles
from .commonfs import write_new_version


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
    with write_new_version(directory, name) as tempfile:
        await overwrite(tempfile, handle)


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
            async for chunk in handle.async_iter_content(chunk_size=8192):
                await fd.write(chunk)
        logger.debug('Wrote: %s', p.as_posix())
    return p.as_posix()