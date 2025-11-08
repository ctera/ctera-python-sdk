from collections import namedtuple
from . import enum
from ..common import Object
from ..exceptions import InputError


TCPService = namedtuple('TCPService', ('host', 'port'))
TCPService.__doc__ = 'Tuple holding the host and port to connect over TCP'
TCPService.host.__doc__ = 'The ip address, hostname or fully qualified domain name of the host'
TCPService.port.__doc__ = 'The port number'


TCPConnectResult = namedtuple('TCPConnectResult', ('host', 'port', 'is_open'))
TCPConnectResult.__doc__ = 'Tuple holding the host and port to connect over TCP'
TCPConnectResult.host.__doc__ = 'The ip address, hostname or fully qualified domain name of the host'
TCPConnectResult.port.__doc__ = 'The port number'
TCPConnectResult.is_open.__doc__ = 'Boolean, indicating whether a TCP connection can be successfully ' \
                                   'established to the target host over the specified port'


StaticRoute = namedtuple('StaticRoute', ('network', 'gateway'))
StaticRoute.__doc__ = 'Tuple holding the network and gateway of a static route'
StaticRoute.network.__doc__ = 'Network (CIDR)'
StaticRoute.gateway.__doc__ = 'Gateway IP address'


class UserGroupEntry():
    """
    User or Group Entry

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    """

    _valid_principal_types = list({k: v for k, v in enum.PrincipalType.__dict__.items() if not k.startswith('_')}.values())

    def __init__(self, principal_type, name):
        UserGroupEntry._validate_principal_type(principal_type)
        self._principal_type = principal_type
        self.name = name

    @property
    def principal_type(self):
        return self._principal_type

    @principal_type.setter
    def principal_type(self, principal_type):
        UserGroupEntry._validate_principal_type(principal_type)
        self._principal_type = principal_type

    def to_server_object(self):
        user_group_obj = Object()
        if self.principal_type == enum.PrincipalType.LU:
            user_group_obj._classname = enum.PrincipalType.LU  # pylint: disable=protected-access
            user_group_obj.ref = "#config#auth#users#" + self.name
        elif self.principal_type == enum.PrincipalType.LG:
            user_group_obj._classname = enum.PrincipalType.LG  # pylint: disable=protected-access
            user_group_obj.ref = "#config#auth#groups#" + self.name
        elif self.principal_type == enum.PrincipalType.DU:
            user_group_obj._classname = enum.PrincipalType.DU  # pylint: disable=protected-access
            user_group_obj.name = self.name
        elif self.principal_type == enum.PrincipalType.DG:
            user_group_obj._classname = enum.PrincipalType.DG  # pylint: disable=protected-access
            user_group_obj.name = self.name
        return user_group_obj

    @staticmethod
    def from_server_object(server_object):
        principal_type = server_object._classname  # pylint: disable=protected-access
        if principal_type in [enum.PrincipalType.LU, enum.PrincipalType.LG]:
            name = server_object.ref
            name = name[name.rfind('#') + 1:]
        else:
            name = server_object.name
        return UserGroupEntry(principal_type, name)

    @staticmethod
    def _validate_principal_type(principal_type):
        if principal_type not in UserGroupEntry._valid_principal_types:
            raise InputError('Invalid principal type', principal_type, UserGroupEntry._valid_principal_types)

    def __str__(self):
        return ('\\' + self.name) if self.principal_type in [enum.PrincipalType.LG, enum.PrincipalType.LU] else self.name


class AccessControlEntryValidator:

    _valid_permissions = list({k: v for k, v in enum.FileAccessMode.__dict__.items() if not k.startswith('_')}.values())

    @staticmethod
    def validate_permission(permission):
        if permission not in AccessControlEntryValidator._valid_permissions:
            raise InputError('Invalid permissions', permission, AccessControlEntryValidator._valid_permissions)


class NFSv3AccessControlEntry():
    """
    NFS v3 export access control entry
    :ivar str address: IP address, hostname or fully qualified domain name of client machine
    :ivar str netmask: Subnet mask
    :ivar cterasdk.edge.enum.FileAccessMode perm: File access permission
    :ivar bool insecure: Allow insecure NFS connections
    """

    def __init__(self, address, netmask, perm, insecure=False):
        AccessControlEntryValidator.validate_permission(perm)
        self._address = address
        self._netmask = netmask
        self._perm = perm
        self._noRootSquash = False
        self._insecure = insecure

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

    @property
    def netmask(self):
        return self._netmask

    @netmask.setter
    def netmask(self, netmask):
        self._netmask = netmask

    @property
    def perm(self):
        return self._perm

    @perm.setter
    def perm(self, perm):
        AccessControlEntryValidator.validate_permission(perm)
        self._perm = perm

    @property
    def insecure(self):
        return self._insecure

    @insecure.setter
    def insecure(self, insecure):
        self._insecure = insecure

    @staticmethod
    def from_server_object(server_object):
        return NFSv3AccessControlEntry(
            server_object.address,
            server_object.netmask,
            server_object.accessLevel,
            getattr(server_object, 'insecure', False)  # Use getattr for backward compatibility
        )

    def to_server_object(self):
        param = Object()
        param.address = self._address
        param.netmask = self._netmask
        param.accessLevel = self._perm
        param.noRootSquash = self._noRootSquash
        param.insecure = self._insecure
        return param

    def __str__(self):
        return str(
            dict(
                address=self._address,
                netmask=self._netmask,
                permission=self._perm,
                insecure=self._insecure
            )
        )


class RemoveNFSv3AccessControlEntry():
    """
    Object holding address and netmasak for NFS v3 export access control entry
    :ivar str address: IP address, hostname or fully qualified domain name of client machine
    :ivar str netmask: Subnet mask
    """

    def __init__(self, address, netmask):
        self._address = address
        self._netmask = netmask

    @property
    def address(self):
        return self._address

    @property
    def netmask(self):
        return self._netmask


class ShareAccessControlEntry():
    """
    Share access control entry for filer shares

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    :ivar cterasdk.edge.enum.FileAccessMode perm: The file access permission
    """

    _valid_permissions = list({k: v for k, v in enum.FileAccessMode.__dict__.items() if not k.startswith('_')}.values())

    def __init__(self, principal_type, name, perm):
        AccessControlEntryValidator.validate_permission(perm)
        self._user_group_entry = UserGroupEntry(principal_type, name)
        self._perm = perm

    @property
    def principal_type(self):
        return self._user_group_entry.principal_type

    @principal_type.setter
    def principal_type(self, principal_type):
        self._user_group_entry.principal_type = principal_type

    @property
    def name(self):
        return self._user_group_entry.name

    @name.setter
    def name(self, name):
        self._user_group_entry.name = name

    @property
    def perm(self):
        return self._perm

    @perm.setter
    def perm(self, perm):
        AccessControlEntryValidator.validate_permission(perm)
        self._perm = perm

    def to_server_object(self):
        ace = Object()
        ace._classname = "ShareACLRule"  # pylint: disable=protected-access
        ace.principal2 = self._user_group_entry.to_server_object()
        ace.permissions = self._create_permissions_object()
        return ace

    def _create_permissions_object(self):
        permissions = Object()
        permissions._classname = "FileAccessPermissions"  # pylint: disable=protected-access
        permissions.allowedFileAccess = self.perm
        return permissions

    @staticmethod
    def from_server_object(server_object):
        user_group_entry = UserGroupEntry.from_server_object(server_object.principal2)
        perm = server_object.permissions.allowedFileAccess
        return ShareAccessControlEntry(user_group_entry.principal_type, user_group_entry.name, perm)


class RemoveShareAccessControlEntry(UserGroupEntry):
    """
    Object holding share access control principal type and name

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    """


class HostCredentials:
    """
    Source Host Credential Object

    :ivar cterasdk.edge.enum.SourceType host_type: Host type
    :ivar str host: Fully qualified domain name, hostname or IP address
    :ivar str username: Source host account username
    :ivar str password: Source host account password
    """

    def __init__(self, host, username, password, host_type=None):
        self._host = host
        self._username = username
        self._password = password
        self._host_type = host_type

    @property
    def host_type(self):
        return self._host_type

    @property
    def host(self):
        return self._host

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @staticmethod
    def localhost():
        return HostCredentials('127.0.0.1', 'dummy', 'dummy', enum.SourceType.Edge)


class DeduplicationStatus(Object):
    """
    Edge Filer Local Deduplication Status Object

    :ivar bool enabled: ``True`` if deduplication is enabled, ``False`` otherwise
    :ivar int size: Logical Size in Bytes
    :ivar int usage: Actual Size in Bytes
    """

    def __init__(self, enabled, size, usage):
        super().__init__()
        self.enabled = enabled
        self.size = size
        self.usage = usage

        savings, dedup = 0, 0
        if self.usage < self.size:
            dedup = self.size - self.usage
            savings = 1 - self.usage / self.size

        self.dedup = dedup
        self.savings = f"{savings:.2%}"


class AntivirusUpdateSchedule(Object):
    """
    Edge Filer Antivirus Update Schedule
    """

    @staticmethod
    def daily(hour, minute):
        """
        Daily update.

        :param int hour: Hour
        :param int minute: Minute
        """
        return AntivirusUpdateSchedule(mode='daily', daily=Object(hour=hour, minute=minute))

    @staticmethod
    def weekly(day, hour, minute):
        """
        Weekly update.

        :param cterasdk.common.enum.DayOfWeek day: Day
        :param int hour: Hour
        :param int minute: Minute
        """
        return AntivirusUpdateSchedule(mode='weekly', weekly=Object(day=day, hour=hour, minute=minute))

    @staticmethod
    def monthly(day, hour, minute):
        """
        Monthly update.

        :param int day: Day
        :param int hour: Hour
        :param int minute: Minute
        """
        return AntivirusUpdateSchedule(mode='monthly', monthly=Object(day=day, hour=hour, minute=minute))


class AlertSettings(Object):  # pylint: disable=too-many-instance-attributes
    """
    Alert Settings

    :ivar bool firmware_upgrade: Enables alerting when a firmware upgrade occurs.
    :ivar bool device_startup: Enables alerting on Edge Filer shutdowns and startups.
    :ivar bool backup_success: Enables alerting upon successful backup completion.
    :ivar bool storage_volume_usage: Enables alerting for high storage volume utilization.
    :ivar int storage_volume_usage_percent: Volume usage percentage threshold that triggers an alert.
    :ivar bool overdue_backup: Enables alerting when a Cloud Backup is overdue.
    :ivar int overdue_backup_days: Number of days since last Cloud Backup after which an alert is triggered.
    :ivar bool delayed_synchronization: Enables alerting when synchronization is delayed.
    :ivar int delayed_synchronization_hours: Number of hours of synchronization delay to trigger an alert.
    :ivar bool disconnected: Enables alerting when the Edge Filer disconnects from the CTERA Portal.
    :ivar int disconnected_hours: Number of hours of disconnection duration to trigger an alert.
    """
    # pylint: disable=too-many-arguments, too-many-locals
    def __init__(self, firmware_upgrade, device_startup, backup_success,
                 storage_volume_usage, storage_volume_usage_percent,
                 overdue_backup, overdue_backup_days,
                 delayed_synchronization, delayed_synchronization_hours,
                 disconnected, disconnected_hours):
        super().__init__()
        self.firmware_upgrade = firmware_upgrade
        self.device_startup = device_startup
        self.backup_success = backup_success
        self.storage_volume_usage = storage_volume_usage
        self.storage_volume_usage_percent = storage_volume_usage_percent
        self.overdue_backup = overdue_backup
        self.overdue_backup_days = overdue_backup_days
        self.delayed_synchronization = delayed_synchronization
        self.delayed_synchronization_hours = delayed_synchronization_hours
        self.disconnected = disconnected
        self.disconnected_hours = disconnected_hours

    def to_server_object(self):
        param = Object()
        param._classname = 'SpecificAlerts'  # pylint: disable=protected-access
        param.NotifyFirmwareUpgrade = self.firmware_upgrade
        param.NotifyDeviceStarted = self.device_startup
        param.NotifyBackupSuccess = self.backup_success
        param.VolumeFullAlert = self.storage_volume_usage
        param.VolumeFullPercent = self.storage_volume_usage_percent
        param.BackupFailAlert = self.overdue_backup
        param.BackupFailDays = self.overdue_backup_days
        param.CloudSyncFailAlert = self.delayed_synchronization
        param.CloudSyncFailHours = self.delayed_synchronization_hours
        param.CloudConnectFailAlert = self.disconnected
        param.CloudConnectFailHours = self.disconnected_hours
        return param

    @staticmethod
    def from_server_object(server_object):
        params = {
            'firmware_upgrade': server_object.NotifyFirmwareUpgrade,
            'device_startup': server_object.NotifyDeviceStarted,
            'backup_success': server_object.NotifyBackupSuccess,
            'storage_volume_usage': server_object.VolumeFullAlert,
            'storage_volume_usage_percent': server_object.VolumeFullPercent,
            'overdue_backup': server_object.BackupFailAlert,
            'overdue_backup_days': server_object.BackupFailDays,
            'delayed_synchronization': server_object.CloudSyncFailAlert,
            'delayed_synchronization_hours': server_object.CloudSyncFailHours,
            'disconnected': server_object.CloudConnectFailAlert,
            'disconnected_hours': server_object.CloudConnectFailHours,
        }
        return AlertSettings(**params)
