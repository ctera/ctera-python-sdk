from abc import ABC
from collections import namedtuple
from ..common import DateTimeUtils

from .enum import PortalAccountType, CollaboratorType, FileAccessMode


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

    @staticmethod
    def from_collaborator(collaborator):
        if collaborator.type == CollaboratorType.LU:
            return UserAccount(collaborator.name)
        if collaborator.type == CollaboratorType.DU:
            return UserAccount(collaborator.name, collaborator.domain)
        if collaborator.type == CollaboratorType.LG:
            return GroupAccount(collaborator.name)
        if collaborator.type == CollaboratorType.DG:
            return GroupAccount(collaborator.name, collaborator.domain)
        return None

    def __eq__(self, other):
        if type(self) is type(other):
            if self.account_type == other.account_type and self.name == other.name and self.directory == other.directory:
                return True
        return False

    def __str__(self):
        return (self.directory if self.directory else '') + '\\' + self.name


class UserAccount(PortalAccount):
    @property
    def account_type(self):
        return PortalAccountType.User


class GroupAccount(PortalAccount):
    @property
    def account_type(self):
        return PortalAccountType.Group


class ShareRecipient:
    """
    Class Representing a Collboration Share Recipient
    """
    def __init__(self, account, account_type, two_factor=False):
        self.account = account
        self.type = account_type
        self.two_factor = two_factor
        self.access = None
        self.expiration_date = None

    @staticmethod
    def external(email, two_factor=False):
        """
        Share with an external user

        :param str email: The email address of the recipient
        :param bool two_factor: Require two factor authentication over e-mail
        """
        return ShareRecipient(email, CollaboratorType.EXT, two_factor)

    @staticmethod
    def local_user(user_account):
        """
        Share with a local user

        :param UserAccount user_account: A local user account
        """
        return ShareRecipient(user_account, CollaboratorType.LU)

    @staticmethod
    def domain_user(user_account):
        """
        Share with a domain user

        :param UserAccount user_account: A domain user account
        """
        return ShareRecipient(user_account, CollaboratorType.DU)

    @staticmethod
    def local_group(group_account):
        """
        Share with a local group

        :param GroupAccount group_account: A local group account
        """
        return ShareRecipient(group_account, CollaboratorType.LG)

    @staticmethod
    def domain_group(group_account):
        """
        Share with a domain group

        :param GroupAccount group_account: A domain group account
        """
        return ShareRecipient(group_account, CollaboratorType.DG)

    def read_write(self):
        """
        Grant read write access
        """
        self.access = FileAccessMode.RW
        return self

    def read_only(self):
        """
        Grant read only access
        """
        self.access = FileAccessMode.RO
        return self

    def preview_only(self):
        """
        Grant preview only access
        """
        self.access = FileAccessMode.PO
        return self

    def no_access(self):
        """
        Deny access
        """
        self.access = FileAccessMode.NA
        return self

    def expire_in(self, days):
        """
        Set share to expire after (days)

        :param int days: The number of days the share will remain accessible
        """
        expiration_date = DateTimeUtils.get_expiration_date(days).strftime('%Y-%m-%d')
        return self.expire_on(expiration_date)

    def expire_on(self, expiration_date):
        """
        Set the share expiration date

        :param str expire_on: The expiration date (%Y-%m-%d)
        """
        self.expiration_date = expiration_date
        return self

    def __str__(self):
        if self.type == CollaboratorType.EXT:
            return self.account
        return str(self.account)
