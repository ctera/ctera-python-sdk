from abc import ABC


class BaseInitializer(ABC):

    def __init__(self, receiver):
        self._receiver = receiver

    def initialize(self):
        command = self._version_selector(self._receiver.session().software_version)
        return command(self._receiver)

    def _version_selector(self, software_version):
        raise NotImplementedError("Subclass must implement the '_version_selector' method")
