from .convert import tojsonstr


class CTERAException(Exception):

    def __init__(self, message=None, instance=None, **kwargs):
        super().__init__()
        self.classname = self.__class__.__name__
        self.join(instance)
        if message is not None:
            self.message = message
        self.put(**kwargs)

    def put(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def join(self, instance=None):
        if instance is not None:
            self.__dict__ = instance.__dict__.copy()

    def __str__(self):
        return tojsonstr(self)


class CTERAClientException(CTERAException):
    pass


class CTERAConnectionError(CTERAException):

    def __init__(self, message, instance, host, port, protocol, **kwargs):
        super().__init__(message, instance, host=host, port=port, protocol=protocol, **kwargs)


class ConnectionTimeout(CTERAException):

    def __init__(self, message, seconds, **kwargs):
        super().__init__(message, None, seconds=seconds, **kwargs)


class HostUnreachable(CTERAConnectionError):

    def __init__(self, instance, host, port, protocol):
        super().__init__("Unable to reach host", instance, host=host, port=port, protocol=protocol)


class ExhaustedException(ConnectionTimeout):

    def __init__(self, retries, timeout):
        super().__init__("Don't blame me for lack of trying", retries * timeout, retries=retries, timeout=timeout)


class PythonVersionException(CTERAException):

    def __init__(self, version):
        super().__init__('You are running an unsupported version of Python', None, version=version)


class SSLException(CTERAConnectionError):

    def __init__(self, host, port, reason):
        super().__init__('Untrusted security certificate', None, host=host, port=port, protocol='TLS', reason=reason)


class ParserException(CTERAException):

    def __init__(self, fmt, payload):
        CTERAException.__init__(self, 'Conversion falied', None, fmt=fmt, to='Python Object', payload=payload)


class InputError(CTERAException):

    def __init__(self, message, expression, options):
        CTERAException.__init__(self, message, None, expression=expression, options=options)


class ConsentException(CTERAException):

    def __init__(self):
        CTERAException.__init__(self, 'Every decision is liberating, even if it leads to disaster')


class FileSystemException(CTERAException):
    pass


class RenameException(FileSystemException):
    def __init__(self, dirpath, src, dst):
        FileSystemException.__init__(self, 'Could not rename file', None, dirpath=dirpath, src=src, dst=dst)


class LocalDirectoryNotFound(FileSystemException):

    def __init__(self, path):
        FileSystemException.__init__(self, 'Could not find local directory', None, path=path)


class LocalFileNotFound(FileSystemException):

    def __init__(self, path):
        FileSystemException.__init__(self, 'Could not find local file', None, path=path)


class LocalPathNotFound(FileSystemException):

    def __init__(self, path):
        FileSystemException.__init__(self, 'Path does not exist', None, path=path)


class RemoteFileSystemException(CTERAException):
    pass


class RemoteDirectoryNotFound(RemoteFileSystemException):

    def __init__(self, path):
        super().__init__('Could not find remote directory', None, path=path)
