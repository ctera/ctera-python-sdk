import logging
from datetime import datetime
from pathlib import Path
from ..common import Object
from ..edge.enum import ResourceError
from ..objects.uri import unquote
from . import common
from .. import exceptions
from .actions import EdgeCommand
from ..lib.storage import synfs, asynfs, commonfs


logger = logging.getLogger('cterasdk.edge')


class EdgePath(common.BasePath):
    """Path for CTERA Edge Filer"""

    def __init__(self, scope, reference):
        """
        Initialize a CTERA Edge Filer Path.

        :param str scope: Scope.
        :param str reference: Reference.
        """
        if isinstance(reference, Object):
            super().__init__(scope, reference.path)
        elif isinstance(reference, str):
            super().__init__(scope, reference)
        elif reference is None:
            super().__init__(scope, '')
        else:
            message = 'Path validation failed: ensure the path exists and is correctly formatted.'
            logger.error(message)
            raise ValueError(message)

    @staticmethod
    def instance(scope, reference):
        if isinstance(reference, tuple):
            source, destination = reference
            return (EdgePath(scope, source), EdgePath(scope, destination))
        return EdgePath(scope, reference)


class Open(EdgeCommand):
    """Open file"""

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = path

    def get_parameter(self):
        return self.path.absolute

    def _before_command(self):
        logger.info('Getting handle: %s', self.path.relative)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class Download(EdgeCommand):

    def __init__(self, function, receiver, path, destination):
        super().__init__(function, receiver)
        self.path = path
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
        return common.encode_request_parameter(param)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class DownloadMany(EdgeCommand):

    def __init__(self, function, receiver, target, objects, destination):
        super().__init__(function, receiver)
        self.target = target
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


def decode_reference(href):
    namespace = '/localFiles'
    return unquote(href[href.index(namespace)+len(namespace) + 1:])


class ListDirectory(EdgeCommand):
    """List"""

    def __init__(self, function, receiver, path, depth=None):
        super().__init__(function, receiver)
        self.path = path
        self.depth = depth if depth is not None else 1

    def _before_command(self):
        logger.info('Listing directory: %s', self.path.relative)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.path.absolute, self.depth)

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.path.absolute, self.depth)

    def _handle_response(self, r):
        entries = []
        for e in r:
            path = decode_reference(e.href)
            if path and self.path != path:
                is_dir = e.getcontenttype == 'httpd/unix-directory'
                param = Object(
                    path=path,
                    name=Path(path).name,
                    is_dir=is_dir,
                    is_file=not is_dir,
                    created_at=e.creationdate,
                    last_modified=datetime.strptime(e.getlastmodified, "%a, %d %b %Y %H:%M:%S GMT").isoformat(),
                    size=e.getcontentlength
                )
                entries.append(param)
        return entries if self.depth > 0 else entries[0]


class RecursiveIterator:

    def __init__(self, function, receiver, path):
        self._function = function
        self._receiver = receiver
        self.path = path
        self.tree = [EdgePath.instance(path.scope, path.relative)]

    def _generator(self):
        while len(self.tree) > 0:
            yield self.tree.pop(0)

    def _before_generate(self):
        EnsureDirectory(self._function, self._receiver, EdgePath.instance(self.path.scope, self.path.relative))
        logger.info('Traversing: %s', self.path.relative)

    def generate(self):
        self._before_generate()
        for path in self._generator():
            for o in ListDirectory(self._function, self._receiver, path).execute():
                if path.relative != o.path:
                    yield self._process_object(o)

    async def a_generate(self):
        self._before_generate()
        for path in self._generator():
            for o in await ListDirectory(self._function, self._receiver, path).a_execute():
                if path.relative != o.path:
                    yield self._process_object(o)

    def _process_object(self, o):
        if o.is_dir:
            self.tree.append(EdgePath.instance(self.path.scope, o))
        return o


class GetMetadata(ListDirectory):

    def __init__(self, function, receiver, path, suppress_error=False):
        super().__init__(function, receiver, path, 0)
        self.suppress_error = suppress_error

    def _before_command(self):
        logger.info('Getting metadata: %s', self.path.relative)

    def _handle_response(self, r):
        return True, super()._handle_response(r)

    def _handle_exception(self, e):
        if not self.suppress_error:
            if isinstance(e, exceptions.transport.NotFound):
                raise exceptions.io.edge.FileNotFoundException(self.path.relative) from e
        return False, None


class EnsureDirectory(EdgeCommand):

    def __init__(self, function, receiver, path, suppress_error=False):
        super().__init__(function, receiver)
        self.path = path
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
        self.path = path
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
                yield EdgePath.instance(self.path.scope, '/'.join(parts[:i]))
        else:
            yield self.path

    def _execute(self):
        with self.trace_execution():
            if self.parents:
                for path in self._parents_generator():
                    try:
                        CreateDirectory(self._function, self._receiver, path).execute()
                    except (exceptions.io.edge.FileConflictError, exceptions.io.edge.ROFSError):
                        pass
            return self._function(self._receiver, self.path.absolute)

    async def _a_execute(self):
        with self.trace_execution():
            if self.parents:
                for path in self._parents_generator():
                    try:
                        await CreateDirectory(self._function, self._receiver, path).a_execute()
                    except (exceptions.io.edge.FileConflictError, exceptions.io.edge.ROFSError):
                        pass
            return await self._function(self._receiver, self.path.absolute)

    def _handle_response(self, r):
        if r == 'OK':
            return self.path.relative
        raise exceptions.io.edge.CreateDirectoryError(self.path.relative)

    def _handle_exception(self, e):
        if e.error.response.error.msg == ResourceError.FileExists:
            raise exceptions.io.edge.FileConflictError(self.path.relative)
        if e.error.response.error.msg == ResourceError.Forbidden:
            raise exceptions.io.edge.ROFSError(self.path.relative)


class Copy(EdgeCommand):
    """Copy"""

    def __init__(self, function, receiver, path, destination=None, overwrite=False):
        super().__init__(function, receiver)
        self.path = path
        self.destination = destination
        self.overwrite = overwrite

    def get_parameter(self):
        if isinstance(self.path, tuple):
            self.path, self.destination = self.path[0], self.path[1]
        else:
            self.path, self.destination = self.path, self.destination.join(self.path.name)
        return (self.path.absolute, self.destination.absolute)

    def _before_command(self):
        logger.info('%s: %s to: %s', 'Copying', self.path.relative, self.destination.relative)

    def _execute(self):
        source, destination = self.get_parameter()
        with self.trace_execution():
            return self._function(self._receiver, source, destination, overwrite=self.overwrite)

    async def _a_execute(self):
        source, destination = self.get_parameter()
        with self.trace_execution():
            return await self._function(self._receiver, source, destination, overwrite=self.overwrite)


class Move(Copy):
    """Move"""

    def _before_command(self):
        logger.info('%s: %s to: %s', 'Moving', self.path.relative, self.destination.relative)


class Rename(Move):
    """Rename"""

    def __init__(self, function, receiver, path, new_name, overwrite=False):
        super().__init__(function, receiver, path, None, overwrite)
        self.new_name = new_name

    def get_parameter(self):
        return (self.path.absolute, self.path.parent.join(self.new_name).absolute)

    def _before_command(self):
        logger.info('Renaming: %s to: %s', self.path.relative, self.path.parent.join(self.new_name).relative)


class Delete(EdgeCommand):

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = path

    def _before_command(self):
        logger.info('Deleting: %s', self.path.relative)

    def _execute(self):
        with self.trace_execution():
            self._function(self._receiver, self.path.absolute)

    async def _a_execute(self):
        with self.trace_execution():
            await self._function(self._receiver, self.path.absolute)


class Upload(EdgeCommand):

    def __init__(self, function, receiver, metadata_function, name, destination, fd):
        super().__init__(function, receiver)
        self._metadata_function = metadata_function
        self.name = name
        self.destination = destination
        self.fd = fd

    def get_parameter(self):
        fd, *_ = common.encode_stream(self.fd, 0)
        param = dict(
            name=self.name,
            fullpath=f'{self.destination.absolute}/{self.name}',
            filedata=fd
        )
        return param

    def _validate_destination(self):
        is_dir, *_ = EnsureDirectory(self._metadata_function, self._receiver, self.destination, True).execute()
        if not is_dir:
            is_dir, *_ = EnsureDirectory(self._metadata_function, self._receiver, self.destination.parent).execute()
            self.name, self.destination = self.destination.name, self.destination.parent

    async def _a_validate_destination(self):
        is_dir, *_ = await EnsureDirectory(self._metadata_function, self._receiver, self.destination, True).a_execute()
        if not is_dir:
            is_dir, *_ = await EnsureDirectory(self._metadata_function, self._receiver, self.destination.parent).a_execute()
            self.name, self.destination = self.destination.name, self.destination.parent

    def _before_command(self):
        logger.info('Uploading: %s', self.destination.join(self.name).relative)

    def _execute(self):
        self._validate_destination()
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        await self._a_validate_destination()
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class UploadFile(EdgeCommand):

    def __init__(self, function, receiver, metadata_function, path, destination):
        super().__init__(function, receiver)
        self._metadata_function = metadata_function
        self.path = path
        self.destination = destination

    def _get_properties(self):
        return commonfs.properties(self.path)

    def _execute(self):
        metadata = self._get_properties()
        with open(self.path, 'rb') as handle:
            with self.trace_execution():
                return Upload(self._function, self._receiver, self._metadata_function, metadata['name'], self.destination, handle).execute()

    async def _a_execute(self):
        metadata = self._get_properties()
        with open(self.path, 'rb') as handle:
            with self.trace_execution():
                return await Upload(self._function, self._receiver, self._metadata_function,
                                    metadata['name'], self.destination, handle).a_execute()
