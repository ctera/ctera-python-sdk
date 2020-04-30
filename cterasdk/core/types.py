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
    def __init__(self):
        self.account = None
        self.type = None
        self.two_factor = False
        self.access = None
        self.expiration_date = None

    def external(self, email, two_factor=False):
        """
        Share with an external user

        :param str email: The email address of the recipient
        :param bool two_factor: Require two factor authentication over e-mail
        """
        self.type = CollaboratorType.EXT
        return self._recipient(email, two_factor)

    def local_user(self, user_account):
        """
        Share with a local user

        :param UserAccount user_account: A local user account
        """
        self.type = CollaboratorType.LU
        return self._recipient(user_account)

    def domain_user(self, user_account):
        """
        Share with a domain user

        :param UserAccount user_account: A domain user account
        """
        self.type = CollaboratorType.DU
        return self._recipient(user_account)

    def local_group(self, group_account):
        """
        Share with a local group

        :param GroupAccount group_account: A local group account
        """
        self.type = CollaboratorType.LG
        return self._recipient(group_account)

    def domain_group(self, group_account):
        """
        Share with a domain group

        :param GroupAccount group_account: A domain group account
        """
        self.type = CollaboratorType.DG
        return self._recipient(group_account)

    def _recipient(self, account, two_factor=False):
        self.account = account
        self.two_factor = two_factor
        return self

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
