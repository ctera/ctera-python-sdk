from abc import ABC
from collections import namedtuple
from ..common import DateTimeUtils, StringCriteriaBuilder, ListCriteriaBuilder, Object

from .enum import PortalAccountType, CollaboratorType, FileAccessMode, PlanCriteria, BucketType, LocationType


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


class PlanCriteriaBuilder:

    Type = 'PlanCriteria'

    @staticmethod
    def username():
        return StringCriteriaBuilder(PlanCriteriaBuilder.Type, PlanCriteria.Username)

    @staticmethod
    def user_groups():
        return ListCriteriaBuilder(PlanCriteriaBuilder.Type, PlanCriteria.Groups)

    @staticmethod
    def role():
        return ListCriteriaBuilder(PlanCriteriaBuilder.Type, PlanCriteria.Role)

    @staticmethod
    def first_name():
        return StringCriteriaBuilder(PlanCriteriaBuilder.Type, PlanCriteria.First)

    @staticmethod
    def last_name():
        return StringCriteriaBuilder(PlanCriteriaBuilder.Type, PlanCriteria.Last)

    @staticmethod
    def company():
        return StringCriteriaBuilder(PlanCriteriaBuilder.Type, PlanCriteria.Company)

    @staticmethod
    def billing_id():
        return StringCriteriaBuilder(PlanCriteriaBuilder.Type, PlanCriteria.BillingId)

    @staticmethod
    def comment():
        return StringCriteriaBuilder(PlanCriteriaBuilder.Type, PlanCriteria.Comment)


class Bucket:

    def __init__(self, bucket, driver):
        self.bucket = bucket
        self.driver = driver

    def to_server_object(self):
        param = Object()
        param.bucket = self.bucket
        param.storage = self.driver
        return param


class HTTPBucket(Bucket):

    def __init__(self, bucket, driver, access_key, secret_key, endpoint, https, direct=False):
        super().__init__(bucket, driver)
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.https = https
        self.direct = direct


class AzureBlob(HTTPBucket):

    def __init__(self, bucket, access_key, secret_key, endpoint='core.windows.net', https=True, direct=True):
        super().__init__(bucket, BucketType.Azure, access_key, secret_key, endpoint, https, direct)

    def to_server_object(self):
        param = super().to_server_object()
        param._classname = LocationType.Azure  # pylint: disable=protected-access
        param.endPoint = self.endpoint
        param.accountName = self.access_key
        param.secretAccess = self.secret_key
        param.useHttps = self.https
        param.directUpload = self.direct
        return param


class S3Compatible(HTTPBucket):

    def __init__(self, bucket, driver, access_key, secret_key,
                 endpoint, https, direct):
        super().__init__(bucket, driver, access_key, secret_key, endpoint, https, direct)

    def to_server_object(self):
        param = super().to_server_object()
        param._classname = LocationType.S3Compatible  # pylint: disable=protected-access
        param.endPoint = self.endpoint
        param.awsAccessKey = self.access_key
        param.awsSecretKey = self.secret_key
        param.useHttps = self.https
        param.directUpload = self.direct
        return param


class Scality(S3Compatible):

    def __init__(self, bucket, access_key, secret_key,
                 endpoint, https=False, direct=False):
        super().__init__(bucket, BucketType.Scality, access_key, secret_key, endpoint, https, direct)


class ICOS(S3Compatible):

    def __init__(self, bucket, access_key, secret_key,
                 endpoint, https=False, direct=False):
        super().__init__(bucket, BucketType.ICOS, access_key, secret_key, endpoint, https, direct)


class Nutanix(S3Compatible):

    def __init__(self, bucket, access_key, secret_key,
                 endpoint, https=False, direct=False):
        super().__init__(bucket, BucketType.Nutanix, access_key, secret_key, endpoint, https, direct)


class Wasabi(S3Compatible):

    def __init__(self, bucket, access_key, secret_key,
                 endpoint, https=False, direct=False):
        super().__init__(bucket, BucketType.Wasabi, access_key, secret_key, endpoint, https, direct)


class Google(S3Compatible):

    def __init__(self, bucket, access_key, secret_key,
                 endpoint, https=False, direct=False):
        super().__init__(bucket, BucketType.Google, access_key, secret_key, endpoint, https, direct)


class GenericS3(S3Compatible):

    def __init__(self, bucket, access_key, secret_key,
                 endpoint, https=False, direct=False):
        super().__init__(bucket, BucketType.S3Compatible, access_key, secret_key, endpoint, https, direct)


class AmazonS3(HTTPBucket):

    def __init__(self, bucket, access_key, secret_key, endpoint='s3.amazonaws.com', https=True, direct=True):
        super().__init__(bucket, BucketType.AWS, access_key, secret_key, endpoint, https, direct)

    def to_server_object(self):
        param = super().to_server_object()
        param._classname = LocationType.S3  # pylint: disable=protected-access
        param.s3Endpoint = self.endpoint
        param.awsAccessKey = self.access_key
        param.awsSecretKey = self.secret_key
        param.httpsOnly = self.https
        param.directUpload = self.direct
        return param
