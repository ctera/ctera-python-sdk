import logging
from ..common import Object
from ...edge.enum import ResourceError
from ..common import encode_request_parameter, encode_stream
from ... import exceptions
from ..actions import EdgeCommand
from ...lib.storage import synfs, asynfs, commonfs
from .types import EdgeResource, automatic_resolution


logger = logging.getLogger('cterasdk.edge')


def split_file_directory(listdir, receiver, destination):
    """
    Split a path into its parent directory and final component.

    :returns:
        tuple[str, str]: A ``(parent_directory, name)`` tuple when:

        * The path refers to an existing file
        * The path refers to an existing directory
        * The parent directory of the path exists

    :raises cterasdk.exceptions.io.edge.GetMetadataError: If neither the path nor its parent directory exist.
    """
    is_dir, *_ = EnsureDirectory(listdir, receiver, destination, True).execute()
    if not is_dir:
        is_dir, *_ = EnsureDirectory(listdir, receiver, destination.parent).execute()
        return destination.parent, destination.name
    return destination, None


async def a_split_file_directory(listdir, receiver, destination):
    """
    Split a path into its parent directory and final component.

    :returns:
        tuple[str, str]: A ``(parent_directory, name)`` tuple when:

        * The path refers to an existing file
        * The path refers to an existing directory
        * The parent directory of the path exists

    :raises cterasdk.exceptions.io.edge.GetMetadataError: If neither the path nor its parent directory exist.
    """
    is_dir, *_ = await EnsureDirectory(listdir, receiver, destination, True).a_execute()
    if not is_dir:
        is_dir, *_ = await EnsureDirectory(listdir, receiver, destination.parent).a_execute()
        return destination.parent, destination.name
    return destination, None


class Open(EdgeCommand):
    """Open file"""

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path)

    def get_parameter(self):
        return self.path.absolute

    def _before_command(self):
        logger.info('Getting handle: %s', self.path)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_exception(self, e):
        path = self.path.relative
        error = exceptions.io.edge.OpenError(path)
        if isinstance(e, exceptions.transport.NotFound):
            raise error from exceptions.io.edge.FileNotFoundException(path)
        raise error


class Download(EdgeCommand):

    def __init__(self, function, receiver, path, destination):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path)
        self.destination = destination

    def get_parameter(self):
        return commonfs.determine_directory_and_filename(self.path.reference, destination=self.destination)

    def _before_command(self):
        logger.info('Downloading: %s', self.path.relative)

    def _execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            with Open(self._function, self._receiver, self.path) as handle:
                return synfs.write(directory, name, handle)

    async def _a_execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            async with Open(self._function, self._receiver, self.path) as handle:
                return await asynfs.write(directory, name, handle)


class OpenMany(EdgeCommand):

    def __init__(self, function, receiver, directory, *objects):
        super().__init__(function, receiver)
        self.directory = directory
        self.objects = objects

    def _before_command(self):
        logger.info('Getting handle: %s', [self.directory.join(o).relative for o in self.objects])

    def get_parameter(self):
        param = Object()
        param.paths = ['/'.join([self.directory.absolute, item]) for item in self.objects]
        param.snapshot = Object()
        param._classname = 'BackupRepository'  # pylint: disable=protected-access
        param.snapshot.location = 1
        param.snapshot.timestamp = None
        param.snapshot.path = None
        logger.info('Getting directory handle: %s', self.directory.reference)
        return encode_request_parameter(param)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class DownloadMany(EdgeCommand):

    def __init__(self, function, receiver, target, objects, destination):
        super().__init__(function, receiver)
        self.target = automatic_resolution(target)
        self.objects = objects
        self.destination = destination

    def get_parameter(self):
        return commonfs.determine_directory_and_filename(self.target.reference, self.objects, destination=self.destination, archive=True)

    def _before_command(self):
        for o in self.objects:
            logger.info('Downloading: %s', self.target.join(o).relative)

    def _execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            with OpenMany(self._function, self._receiver, self.target, *self.objects) as handle:
                return synfs.write(directory, name, handle)

    async def _a_execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            async with OpenMany(self._function, self._receiver, self.target, *self.objects) as handle:
                return await asynfs.write(directory, name, handle)


class ListDirectory(EdgeCommand):
    """List"""

    def __init__(self, function, receiver, path, depth=None):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path)
        self.depth = depth if depth is not None else 1

    def _before_command(self):
        logger.info('Listing directory: %s', self.path)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.path.absolute, self.depth)

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.path.absolute, self.depth)

    def _handle_response(self, r):
        if self.depth <= 0:
            return EdgeResource.from_server_object(r[0])
        return [EdgeResource.from_server_object(e) for e in r if self.path.relative != EdgeResource.decode_reference(e.href)]

    def _handle_exception(self, e):
        path = self.path.relative
        error = exceptions.io.edge.ListDirectoryError(path)
        if isinstance(e, exceptions.transport.NotFound):
            raise error from exceptions.io.edge.FolderNotFoundError(path)
        raise error from e


class RecursiveIterator:

    def __init__(self, function, receiver, path):
        self._function = function
        self._receiver = receiver
        self.path = automatic_resolution(path)
        self.tree = [self.path]

    def _generator(self):
        logger.info('Traversing: %s', self.path)
        while len(self.tree) > 0:
            yield self.tree.pop(0)

    def generate(self):
        for path in self._generator():
            try:
                for o in ListDirectory(self._function, self._receiver, path).execute():
                    if path.relative != o.path.relative:
                        yield self._process_object(o)
            except exceptions.io.edge.ListDirectoryError as e:
                RecursiveIterator._suppress_error(e)

    async def a_generate(self):
        for path in self._generator():
            try:
                for o in await ListDirectory(self._function, self._receiver, path).a_execute():
                    if path.relative != o.path.relative:
                        yield self._process_object(o)
            except exceptions.io.edge.ListDirectoryError as e:
                RecursiveIterator._suppress_error(e)

    def _process_object(self, o):
        if o.is_dir:
            self.tree.append(o.path)
        return o

    @staticmethod
    def _suppress_error(e):
        if not isinstance(e.__cause__, exceptions.io.edge.FolderNotFoundError):
            raise e
        logger.warning("Could not list directory contents: %s. No such directory.", e.path)


class GetMetadata(ListDirectory):

    def __init__(self, function, receiver, path, suppress_error=False):
        super().__init__(function, receiver, path, 0)
        self.suppress_error = suppress_error

    def _before_command(self):
        logger.info('Getting metadata: %s', self.path.relative)

    def _handle_response(self, r):
        return True, super()._handle_response(r)

    def _handle_exception(self, e):
        path = self.path.relative
        if not self.suppress_error:
            if isinstance(e, exceptions.transport.NotFound):
                cause = exceptions.io.edge.ObjectNotFoundError(path)
                raise exceptions.io.edge.GetMetadataError(path) from cause
        return False, None


class EnsureDirectory(EdgeCommand):

    def __init__(self, function, receiver, path, suppress_error=False):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path)
        self.suppress_error = suppress_error

    def _execute(self):
        return GetMetadata(self._function, self._receiver, self.path, self.suppress_error).execute()

    async def _a_execute(self):
        return await GetMetadata(self._function, self._receiver, self.path, self.suppress_error).a_execute()

    def _handle_response(self, r):
        exists, resource = r if r is not None else (False, None)
        if (not exists or not resource.is_dir) and not self.suppress_error:
            raise exceptions.io.edge.NotADirectoryException(self.path.relative)
        return resource.is_dir if exists else False, resource


class CreateDirectory(EdgeCommand):
    """Create Directory"""

    def __init__(self, function, receiver, path, parents=False):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path)
        self.parents = parents

    def get_parameter(self):
        param = Object()
        param.name = self.path.name
        param.parentPath = self.path.parent.absolute_encode
        return param

    def _before_command(self):
        logger.info('Creating directory: %s', self.path.relative)

    def _parents_generator(self):
        if self.parents:
            parts = self.path.parts
            for i in range(1, len(parts)):
                yield automatic_resolution('/'.join(parts[:i]))
        else:
            yield self.path

    def _execute(self):
        if self.parents:
            for path in self._parents_generator():
                try:
                    CreateDirectory(self._function, self._receiver, path).execute()
                except exceptions.io.edge.CreateDirectoryError as e:
                    CreateDirectory._suppress_error(e)
        with self.trace_execution():
            return self._function(self._receiver, self.path.absolute)

    async def _a_execute(self):
        if self.parents:
            for path in self._parents_generator():
                try:
                    await CreateDirectory(self._function, self._receiver, path).a_execute()
                except exceptions.io.edge.CreateDirectoryError as e:
                    CreateDirectory._suppress_error(e)
        with self.trace_execution():
            return await self._function(self._receiver, self.path.absolute)

    def _handle_response(self, r):
        if r is None or not r or r == 'OK':
            return self.path.relative
        raise exceptions.io.edge.CreateDirectoryError(self.path.relative)

    def _handle_exception(self, e):
        path = self.path.relative
        error = exceptions.io.edge.CreateDirectoryError(path)
        if e.error.response.error.msg == ResourceError.FileExists:
            raise error from exceptions.io.edge.FileConflictError(path)
        if e.error.response.error.msg == ResourceError.Forbidden:
            raise error from exceptions.io.edge.ROFSError(path)
        raise error from e

    @staticmethod
    def _suppress_error(e):
        if not isinstance(e.__cause__, (exceptions.io.edge.FileConflictError, exceptions.io.edge.ROFSError)):
            raise e


class Copy(EdgeCommand):
    """Copy"""

    def __init__(self, function, receiver, listdir, path, destination, overwrite):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path)
        self.destination = automatic_resolution(destination)
        self._resolver = PathResolver(listdir, receiver, self.destination, self.path.name)
        self.overwrite = overwrite

    def get_parameter(self):
        return self.path.absolute, self.destination.absolute

    def _before_command(self):
        if self.path == self.destination:
            logger.info('No-op copy. Source and destination refer to the same file: %s', self.path.relative)
            raise self._error_object() from exceptions.io.edge.FileConflictError(self.path.relative)
        logger.info('%s: %s to: %s', 'Copying', self.path.relative, self.destination.relative)

    def _execute(self):
        self.destination = self._resolver.resolve()
        source, destination = self.get_parameter()
        with self.trace_execution():
            return self._function(self._receiver, source, destination, overwrite=self.overwrite)

    async def _a_execute(self):
        self.destination = await self._resolver.a_resolve()
        source, destination = self.get_parameter()
        with self.trace_execution():
            return await self._function(self._receiver, source, destination, overwrite=self.overwrite)

    def _error_object(self):
        return exceptions.io.edge.CopyError(self.path.relative, self.destination.relative)

    def _file_conflict(self):
        return exceptions.io.edge.FileConflictError(self.destination.relative)

    def _handle_response(self, r):
        return self.destination.relative

    def _handle_exception(self, e):
        error = self._error_object()
        if isinstance(e, (exceptions.transport.PreConditionFailed, exceptions.transport.Conflict)):
            raise error from self._file_conflict()
        raise error


class Move(Copy):
    """Move"""

    def _before_command(self):
        logger.info('%s: %s to: %s', 'Moving', self.path.relative, self.destination.relative)

    def _error_object(self):
        return exceptions.io.edge.MoveError(self.path.relative, self.destination.relative)


class Rename(Move):
    """Rename"""

    def __init__(self, function, receiver, listdir, path, new_name, overwrite):
        super().__init__(function, receiver, listdir, path, automatic_resolution(path).parent.join(new_name), overwrite)
        self.new_name = new_name

    def _before_command(self):
        logger.info('%s: %s to: %s', 'Renaming', self.path.relative, self.destination.relative)

    def _error_object(self):
        return exceptions.io.edge.RenameError(self.path.relative, self.new_name)

    def _file_conflict(self):
        return exceptions.io.edge.FileConflictError(self.destination.relative)


class Delete(EdgeCommand):

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path)

    def _before_command(self):
        logger.info('Deleting: %s', self.path.relative)

    def _execute(self):
        with self.trace_execution():
            self._function(self._receiver, self.path.absolute)

    async def _a_execute(self):
        with self.trace_execution():
            await self._function(self._receiver, self.path.absolute)

    def _handle_response(self, r):
        return self.path.relative

    def _handle_exception(self, e):
        path = self.path.relative
        error = exceptions.io.edge.DeleteError(path)
        if isinstance(e, exceptions.transport.NotFound):
            raise error from exceptions.io.edge.ObjectNotFoundError(path)
        raise error


class PathResolver:

    def __init__(self, listdir, receiver, destination, default):
        self._listdir = listdir
        self._receiver = receiver
        self._destination = destination
        self._default = default

    async def a_resolve(self):
        parent, name = await a_split_file_directory(self._listdir, self._receiver, self._destination)
        return self._resolve(parent, name)

    def resolve(self):
        parent, name = split_file_directory(self._listdir, self._receiver, self._destination)
        return self._resolve(parent, name)

    def _resolve(self, parent, name):
        if name is not None:
            return parent.join(name)
        if self._default is not None:
            return parent.join(self._default)
        return self._destination


class Upload(EdgeCommand):

    def __init__(self, function, receiver, listdir, destination, fd, name):
        super().__init__(function, receiver)
        self.destination = automatic_resolution(destination)
        self._resolver = PathResolver(listdir, receiver, self.destination, name)
        self.fd = fd

    def get_parameter(self):
        fd, *_ = encode_stream(self.fd, 0)
        param = dict(
            name=self.destination.name,
            fullpath=f'{self.destination.absolute}',
            filedata=fd
        )
        return param

    def _before_command(self):
        logger.info('Uploading: %s', self.destination.relative)

    def _execute(self):
        self.destination = self._resolver.resolve()
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter()).xml()

    async def _a_execute(self):
        self.destination = await self._resolver.a_resolve()
        with self.trace_execution():
            response = await self._function(self._receiver, self.get_parameter())
            return await response.xml()

    def _handle_response(self, r):
        if r.rc != 0:
            raise exceptions.io.edge.UploadError(r.msg, self.destination.relative)
        return self.destination.relative

    def _handle_exception(self, e):
        raise exceptions.io.edge.UploadError(e.error.msg, self.destination.relative) from e
