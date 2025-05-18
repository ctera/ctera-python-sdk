import os
import errno
import logging
import mimetypes
from pathlib import Path
from contextlib import contextmanager
import cterasdk.settings


logger = logging.getLogger('cterasdk.filesystem')


def exists(path):
    """
    Check if a file or a directory exists

    :param str path: Path
    :returns: ``True`` if exists, ``False`` otherwise.
    :rtype: bool
    """
    return Path(path).exists()


def expanduser(path):
    """
    Return a new path with expanded ~ and ~user constructs

    :param str path: Path
    :returns: Absolute Path.
    :rtype: Path object
    """
    return Path(path).expanduser()


def is_dir(path):
    """
    Check is a directory.

    :param str path: Path
    :returns: ``True`` if a directory, ``False`` otherwise.
    :rtype: bool
    """
    p = expanduser(path)
    return p.is_dir()


def join(*paths):
    """
    Join Path objects.

    :param list[Path] paths: Path objects
    :rtype: Path
    """
    return Path(*paths)


def properties(path):
    """
    File properties.

    :param str path: Path
    :returns: File name, size and type
    :rtype: dict
    :raises: FileNotFoundError
    """
    p = expanduser(path)

    if not p.exists() or not p.is_file():
        logger.error('File not found: %s', p.as_posix())
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p.as_posix())

    return dict(
        name=p.name,
        size=str(p.stat().st_size),
        mimetype=mimetypes.guess_type(path)
    )


def downloads():
    """
    Get downloads directory.

    :returns: Directory path
    :rtype: Path object
    """
    directory = expanduser(cterasdk.settings.io.downloads)
    if not is_dir(directory):
        logger.error('Directory not found: %s', directory)
        raise FileNotFoundError(errno.ENOENT, 'Directory not found', directory)
    return directory


def determine_zip_archive_name(directory, objects):
    """
    Name the zip archive after the folder name, unless the directory contains only one object.

    :rtype: str
    """
    if len(objects) > 1:
        path = Path(directory)
    else:
        path = Path(objects[0])
    return f'{path.stem}.zip'


def new_version(filename, version):
    """
    Append version number to file name.

    :param str filename: File name
    :param int version: File version
    :returns: File name appended with a version number
    :rtype: str
    """
    idx = filename.rfind('.')
    extension = ''
    if idx > 0:
        name = filename[:idx]
        extension = filename[idx:]
    else:
        name = filename
    return f'{name} ({str(version)}){extension}'


def rename(source, new_name):
    """
    Rename a file or a directory.

    :param str source: Path
    :param str new_name: New name
    :returns: Path after rename
    :rtype: str
    """
    source = expanduser(source)
    if not source.exists():
        logger.error('File not found: %s', source.as_posix())
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), source.as_posix())
    destination = source.parent.joinpath(new_name)
    source.rename(destination)
    return destination.as_posix()


class ResultContext:
    """Context Manager Result Context"""

    def __init__(self):
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v


@contextmanager
def write_new_version(directory, name, *, ctx=None):
    """
    Context manager for writing a file without conflicts.

    :param str directory: Parent directory
    :param str name: File name
    :param ResultContext,optional ctx: Result Context
    :returns: Path
    :rtype: str
    :raises: FileNotFoundError
    """
    parent = expanduser(directory)
    if not parent.exists() or not is_dir(parent):
        logger.error('Directory not found: %s', parent.as_posix())
        raise FileNotFoundError(errno.ENOENT, 'Directory not found', directory)

    tempfile = parent.joinpath(f'{name}.ctera')
    yield tempfile

    origin, version = name, 0
    while True:
        try:
            rename(tempfile, name)
            break
        except (FileExistsError, IsADirectoryError):
            logger.debug('File exists: %s', parent.joinpath(name))
            version = version + 1
            name = new_version(origin, version)

    p = parent.joinpath(name)
    logger.info('Saved: %s', p.as_posix())

    if ctx and isinstance(ctx, ResultContext):
        ctx.value = p.as_posix()


def split_file_directory(location):
    """
    Split file and directory.

    :param str path: Path

    Returns:
    1. (parent directory, file name), if a file exists
    2. (parent directory, file name), if a directory exists
    3. (parent directory, file name), if the parent directory exists
    4. Raises ``FileNotFoundError`` if neither the object nor the parent directory exist
    """
    p = expanduser(location)
    if p.exists():
        if p.is_dir():
            filename = None
        else:
            filename = p.name
            p = p.parent
    elif p.parent.exists():
        filename = p.name
        p = p.parent
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), location)
    return str(p.resolve()), filename


def generate_file_destination(destination=None, default_name=None):
    """
    Compute destination file path.

    :param str location: Path to a file or a folder
    :param str default_name: Default file name, unless ``location`` already specifies a file path
    :returns: Tuple including the destination directory and file name
    :rtype: tuple(str, str)
    """
    parent = name = None
    if destination:
        parent, name = split_file_directory(destination)
    else:
        parent = downloads()

    if not name:
        name = default_name

    return (parent, name)


def determine_directory_and_filename(p, objects=None, destination=None, archive=False):
    """
    Determine location to save file.

    :param str p: Path.
    :param list[str],optional objects: List of files or folders
    :param str,optional destination: Destination
    :param bool,optional archive: Compressed archive
    :returns: Directory and file name
    :rtype: tuple[str]
    """
    directory, name = None, None
    if destination:
        directory, name = split_file_directory(destination)
    else:
        directory = downloads()

    if not name:
        normalized = Path(p)
        if archive:
            name = determine_zip_archive_name(p, objects)
        else:
            name = normalized.name
    return directory, name
