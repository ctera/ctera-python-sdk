import logging
from abc import ABC, abstractmethod
from .utils import Version


logger = logging.getLogger('cterasdk.common')


class BaseModule(ABC):

    @abstractmethod
    def initialize_version(self, software_version):
        raise NotImplementedError("Subclass must implement the 'initialize_version' method.")


def initialize(module_class, receiver):
    session = receiver.session()
    software_version = session.software_version if session.software_version else Version('0')
    concrete_class = module_class().initialize_version(software_version)
    logger.debug('Initializing: %s', concrete_class.__name__)
    return concrete_class(receiver)
