from abc import ABC
from collections import namedtuple
from ..common import DateTimeUtils, StringCriteriaBuilder, ListCriteriaBuilder, Object
from ..lib import FileSystem

from .enum import PortalAccountType, CollaboratorType, FileAccessMode, PlanCriteria, TemplateCriteria, \
                  BucketType, LocationType, Platform, RetentionMode, Duration


CloudFSFolderFindingHelper = namedtuple('CloudFSFolderFindingHelper', ('name', 'owner'))
CloudFSFolderFindingHelper.__doc__ = 'Tuple holding the name and owner couple to search for folders'
CloudFSFolderFindingHelper.name.__doc__ = 'The name of the CloudFS folder'
CloudFSFolderFindingHelper.owner.__doc__ = 'The name of the owner of the CloudFS folder'


PlatformVersion = namedtuple('PlatformVersion', ('name', 'version'))
PlatformVersion.__doc__ = 'Tuple holding the platform name and version'
PlatformVersion.name.__doc__ = 'The name of the platform'
PlatformVersion.version.__doc__ = 'The version identifier'


AccessControlEntry = namedtuple('AccessControlEntry', ('account', 'role'))
AccessControlEntry.__doc__ = 'Tuple holding a Portal account and its respective permission'
AccessControlEntry.account.__doc__ = 'The Portal group or user account'
AccessControlEntry.role.__doc__ = 'The group or user role'


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


class TemplateCriteriaBuilder:

    Type = 'DeviceCriteria'

    @staticmethod
    def type():
        return ListCriteriaBuilder(TemplateCriteriaBuilder.Type, TemplateCriteria.Type)

    @staticmethod
    def os():
        return StringCriteriaBuilder(TemplateCriteriaBuilder.Type, TemplateCriteria.OperatingSystem)

    @staticmethod
    def version():
        return StringCriteriaBuilder(TemplateCriteriaBuilder.Type, TemplateCriteria.Version)

    @staticmethod
    def hostname():
        return StringCriteriaBuilder(TemplateCriteriaBuilder.Type, TemplateCriteria.Hostname)

    @staticmethod
    def name():
        return StringCriteriaBuilder(TemplateCriteriaBuilder.Type, TemplateCriteria.Name)

    @staticmethod
    def owner():
        return StringCriteriaBuilder(TemplateCriteriaBuilder.Type, TemplateCriteria.Owner)

    @staticmethod
    def plan():
        return StringCriteriaBuilder(TemplateCriteriaBuilder.Type, TemplateCriteria.Plan)

    @staticmethod
    def groups():
        return StringCriteriaBuilder(TemplateCriteriaBuilder.Type, TemplateCriteria.Groups)


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
        super().__init__(bucket, BucketType.GenericS3, access_key, secret_key, endpoint, https, direct)


class NetAppStorageGRID(S3Compatible):

    def __init__(self, bucket, access_key, secret_key,
                 endpoint, https=False, direct=False, tags=False):
        super().__init__(bucket, BucketType.NetAppStorageGRID, access_key, secret_key, endpoint, https, direct)
        self.tagBlocks = tags

    def to_server_object(self):
        param = super().to_server_object()
        param._classname = LocationType.NetAppStorageGRID  # pylint: disable=protected-access
        return param


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


class DomainControllers:

    def __init__(self, primary=None, secondary=None):
        self._primary = primary
        self._secondary = secondary

    @property
    def primary(self):
        return self._primary

    @property
    def secondary(self):
        return self._secondary


class AccessControlRule(Object):

    def __init__(self, group, role):
        self._classname = 'AccessControlRule'
        self.group = group
        self.role = role


class TemplateScript:

    def __init__(self, platform):
        self._platform = platform
        self._after_logon = None
        self._before_backup = None
        self._after_backup = None

    @property
    def platform(self):
        return self._platform

    @staticmethod
    def windows():
        """
        Configure Windows Scripts
        """
        return TemplateScript(Platform.Windows)

    @staticmethod
    def linux():
        """
        Configure Windows Scripts
        """
        return TemplateScript(Platform.Linux)

    @staticmethod
    def mac():
        """
        Configure Windows Scripts
        """
        return TemplateScript(Platform.OSX)

    def after_logon(self, after_logon):
        """
        Set the post logon script

        :param str after_logon: A string or path to the script file
        """
        self._after_logon = TemplateScript._get_contents(after_logon)
        return self

    def before_backup(self, before_backup):
        """
        Set the pre backup script

        :param str before_backup: A string or path to the script file
        """
        self._before_backup = TemplateScript._get_contents(before_backup)
        return self

    def after_backup(self, after_backup):
        """
        Set the post backup script

        :param str after_backup: A string or path to the script file
        """
        self._after_backup = TemplateScript._get_contents(after_backup)
        return self

    @staticmethod
    def _get_contents(shell_script):
        if FileSystem.instance().exists(shell_script):
            with open(shell_script, 'r', encoding='utf-8') as f:
                data = f.read()
            return data
        return shell_script

    def to_server_object(self):
        param = Object()
        param._classname = 'OsScriptTemplates'  # pylint: disable=protected-access
        if self._before_backup is not None:
            param.beforeBackup = self._before_backup
        if self._after_backup is not None:
            param.afterBackup = self._after_backup
        if self._after_logon is not None:
            param.afterFirtSignIn = self._after_logon
        return param


class AlertBuilder:

    def __init__(self, name):
        self.param = Object()
        self.param._classname = 'AlertRule'
        self.param.id = name

    @staticmethod
    def name(name):
        """
        Create an Alert Builder

        :param str name: Alert name
        :returns: Alert Builder
        :rtype: cterasdk.core.types.AlertBuilder
        """
        return AlertBuilder(name)

    def description(self, description):
        """
        Set alert description

        :param str description: Alert description
        :returns: Alert Builder
        :rtype: cterasdk.core.types.AlertBuilder
        """
        self.param.description = description
        return self

    def log(self, log):
        """
        Set alert log class name

        :param str log: Log class name
        :returns: Alert Builder
        :rtype: cterasdk.core.types.AlertBuilder
        """
        self.param.logName = log
        return self

    def topic(self, topic):
        """
        Set alert log topic

        :param cterasdk.core.enum.LogTopic topic: Log topic
        :returns: Alert Builder
        :rtype: cterasdk.core.types.AlertBuilder
        """
        self.param.topic = topic
        return self

    def min_severity(self, min_severity):
        """
        Set alert log minimum severity

        :param cterasdk.core.enum.Severity min_severity: Minimum severity
        :returns: Alert Builder
        :rtype: cterasdk.core.types.AlertBuilder
        """
        self.param.minSeverity = min_severity
        return self

    def origin_type(self, origin_type):
        """
        Set alert origin type

        :param cterasdk.core.enum.OriginType origin_type: Log origin type
        :returns: Alert Builder
        :rtype: cterasdk.core.types.AlertBuilder
        """
        self.param.originType = origin_type
        return self

    def content(self, content):
        """
        Set alert log message content

        :param str content: Log content
        :returns: Alert Builder
        :rtype: cterasdk.core.types.AlertBuilder
        """
        self.param.messageContent = content
        return self

    def build(self):
        """
        Build the alert

        :returns: Alert object
        :rtype: cterasdk.common.object.Object
        """
        return self.param


class Task(Object):

    def __init__(self, task_id, name):
        self.id = task_id
        self.name = name


class ScheduledTask(Task):

    def __init__(self, task_id, name, start_time):
        super().__init__(task_id, name)
        self.start_time = start_time

    @staticmethod
    def from_server_object(server_object):
        return ScheduledTask(
            server_object.id,
            server_object.name,
            server_object.startTime,
        )


class BackgroundTask(Task):

    def __init__(self, task_id, name, start_time, end_time, elapsed_time, status, message, ref):
        super().__init__(task_id, name)
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.status = status
        self.message = message
        self.ref = ref

    @staticmethod
    def from_server_object(server_object, ref):
        return BackgroundTask(
            server_object.id,
            server_object.name,
            server_object.startTime,
            server_object.endTime,
            server_object.elapsedTime,
            server_object.status,
            server_object.progstring,
            ref
        )


class ComplianceSettingsBuilder:

    def __init__(self, enabled, mode, retain_for):
        self.settings = Object()
        self.settings._classname = 'WormSettings'  # pylint: disable=protected-access
        self.settings.worm = enabled
        self.settings.retentionMode = mode
        self.settings.retentionPeriod = retain_for
        self.settings.gracePeriod = None

    @staticmethod
    def default():
        return ComplianceSettingsBuilder(False, RetentionMode.Delete, None)

    @staticmethod
    def none(amount, duration):
        return ComplianceSettingsBuilder(True, RetentionMode.Delete, ComplianceSettingsBuilder._get_retention_period(amount, duration))

    @staticmethod
    def enterprise(amount, duration):
        return ComplianceSettingsBuilder(True, RetentionMode.Enterprise, ComplianceSettingsBuilder._get_retention_period(amount, duration))

    @staticmethod
    def compliance(amount, duration):
        return ComplianceSettingsBuilder(True, RetentionMode.Compliance, ComplianceSettingsBuilder._get_retention_period(amount, duration))

    @staticmethod
    def _get_retention_period(amount, duration):
        retain_for = Object()
        retain_for._classname = 'WormPeriod'  # pylint: disable=protected-access
        retain_for.amount = amount
        retain_for.type = duration
        return retain_for

    def grace_period(self, amount=30, duration=Duration.Minutes):
        self.settings.gracePeriod = self._get_retention_period(amount, duration)
        return self

    def build(self):
        if self.settings.gracePeriod is None:
            self.grace_period()
        return self.settings


class RoleSettings(Object):  # pylint: disable=too-many-instance-attributes
    """
    Role Settings

    :ivar str name: Role name
    :ivar bool sudo: Super user
    :ivar bool enable_remote_wipe: Allow Remote Wipe for Devices
    :ivar bool enable_sso: Super user
    :ivar bool enable_seeding_export: Allow Seeding Export
    :ivar bool enable_seeding_import: Allow Seeding Import
    :ivar bool access_end_user_folders: Access End User Folders
    :ivar bool update_settings: Modify Virtual Portal Settings
    :ivar bool update_roles: Modify Roles
    :ivar bool update_account_emails: Modify User Email
    :ivar bool update_account_password: Modify User Password
    :ivar bool manage_cloud_drives: Manage Cloud Folders
    :ivar bool manage_plans: Manage Plans
    :ivar bool manage_logs: Manage Log Settings
    """
    # pylint: disable=too-many-arguments, too-many-locals
    def __init__(self, name, sudo, enable_remote_wipe, enable_sso, enable_seeding_export, enable_seeding_import, access_end_user_folders,
                 update_settings, update_roles, update_account_emails, update_account_password, manage_cloud_drives, manage_plans,
                 manage_users, manage_logs):
        self.name = name
        self.sudo = sudo
        self.enable_remote_wipe = enable_remote_wipe
        self.enable_sso = enable_sso
        self.enable_seeding_export = enable_seeding_export
        self.enable_seeding_import = enable_seeding_import
        self.access_end_user_folders = access_end_user_folders
        self.update_settings = update_settings
        self.update_roles = update_roles
        self.update_account_emails = update_account_emails
        self.update_account_password = update_account_password
        self.manage_cloud_drives = manage_cloud_drives
        self.manage_plans = manage_plans
        self.manage_users = manage_users
        self.manage_logs = manage_logs

    def to_server_object(self):
        param = Object()
        param._classname = 'PortalRoleSettings'  # pylint: disable=protected-access
        param.name = self.name
        param.superUser = self.sudo
        param.allowRemoteWipe = self.enable_remote_wipe
        param.allowSSO = self.enable_sso
        param.allowSeedingExport = self.enable_seeding_export
        param.allowSeedingImport = self.enable_seeding_import
        param.canAccessEndUserFolders = self.access_end_user_folders
        param.canChangePortalSettings = self.update_settings
        param.canChangeRoles = self.update_roles
        param.canChangeUserEmail = self.update_account_emails
        param.canChangeUserPassword = self.update_account_password
        param.canManageAllFolders = self.manage_cloud_drives
        param.canManagePlans = self.manage_plans
        param.canManageUsers = self.manage_users
        param.canManageLogSettings = self.manage_logs
        return param

    @staticmethod
    def from_server_object(server_object):
        params = {
            'name': server_object.name,
            'sudo': server_object.superUser,
            'enable_remote_wipe': server_object.allowRemoteWipe,
            'enable_sso': server_object.allowSSO,
            'enable_seeding_export': server_object.allowSeedingExport,
            'enable_seeding_import': server_object.allowSeedingImport,
            'access_end_user_folders': server_object.canAccessEndUserFolders,
            'update_settings': server_object.canChangePortalSettings,
            'update_roles': server_object.canChangeRoles,
            'update_account_emails': server_object.canChangeUserEmail,
            'update_account_password': server_object.canChangeUserPassword,
            'manage_cloud_drives': server_object.canManageAllFolders,
            'manage_plans': server_object.canManagePlans,
            'manage_users': server_object.canManageUsers,
            'manage_logs': server_object.canManageLogSettings
        }
        return RoleSettings(**params)
