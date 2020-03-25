from abc import ABC
from collections import namedtuple

from .enum import PortalAccountType


CloudFSFolderFindingHelper = namedtuple('CloudFSFolderFindingHelper', ('name', 'owner'))
CloudFSFolderFindingHelper.__doc__ = 'Tuple holding the name and owner couple to search for folders'
CloudFSFolderFindingHelper.name.__doc__ = 'The name of the CloudFS folder'
CloudFSFolderFindingHelper.owner.__doc__ = 'The name of the owner of the CloudFS folder'


class PortalAccount(ABC):
    """
    Base Class for Portal Account

    :ivar str name: The user name
    :ivar str directory: The fully-qualified name of the user directory, defaults to None
    """
    def __init__(self, name, directory=None):
        """
        :param str name: The name of the Portal user
        :param str directory: The the fully qualified domain name, defaults to None
        """
        self.name = name
        self.directory = directory

    @property
    def is_local(self):
        """
        Is the account local

        :return bool: True if the account if local, otherwise False
        """
        return not self.directory

    @property
    def account_type(self):
        """
        The Portal Account Type

        :return cterasdk.core.enum.PortalAccountType: The Portal Account Type
        """
        raise NotImplementedError('Implementing class much implement the account_type property')


class UserAccount(PortalAccount):
    @property
    def account_type(self):
        return PortalAccountType.User


class GroupAccount(PortalAccount):
    @property
    def account_type(self):
        return PortalAccountType.Group
