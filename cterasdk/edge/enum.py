class Mode:
    """
    Enum for operational mode

    :ivar str Enabled: Operational mode enabled
    :ivar str Disabled: Operational mode diabled
    """
    Enabled = "enabled"
    Disabled = "disabled"


class IPProtocol:
    """
    IP Protocol

    :ivar str TCP: TCP Protocol
    :ivar str UDP: UDP Protocol
    """
    TCP = "TCP"
    UDP = "UDP"


class Severity:
    """
    Log severity levels

    :ivar str EMERGENCY: Emergency log level
    :ivar str ALERT: Alert log level
    :ivar str CRITICAL: Critical log level
    :ivar str ERROR: Error log level
    :ivar str WARNING: Warning log level
    :ivar str NOTICE: Notice log level
    :ivar str INFO: Info log level
    :ivar str DEBUG: Debug log level
    """
    EMERGENCY = "emergency"
    ALERT = "alert"
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"
    INFO = "info"
    DEBUG = "debug"


class VolumeStatus:
    """
    Gateway volume status

    :ivar str Ok: Volume is ok
    :ivar str ContainsErrors: Volume contains errors
    :ivar str ReadOnly: Voilume is read only
    :ivar str Corrupted: Volume is corrupted"
    :ivar str Unknown: Volume status is unknown
    :ivar str Recovering: Volume is recovering
    :ivar str Mounting: Volume is mounting
    :ivar str Unmounted: Volume is unmounted
    :ivar str Formatting: Volume is formatting
    :ivar str Converting: Volume is converting
    :ivar str Resizing: Volume is resizing
    :ivar str Repairing: Volume is repairing
    :ivar str Checking: Volume is checking
    :ivar str KeyRequired: Volume required key
    :ivar str CheckingQuota: Checking volume  quota
    """
    Ok = "ok"
    ContainsErrors = "containsErrors"
    ReadOnly = "readOnly"
    Corrupted = "corrupted"
    Unknown = "unknown"
    Recovering = "recovering"
    Mounting = "mounting"
    Unmounted = "unmounted"
    Formatting = "formatting"
    Converting = "converting"
    Resizing = "resizing"
    Repairing = "repairing"
    Checking = "checking"
    KeyRequired = "keyRequired"
    CheckingQuota = "checkingQuota"


class CIFSPacketSigning:
    """
    CIFS Packet signing options

    :ivar str Disabled: CIFS Packet signing is disabled
    :ivar str IfClientAgrees: Use CIFS Packet signing is client agrees
    :ivar str Required: Require CIFS Packet signing
    """
    Disabled = "Disabled"
    IfClientAgrees = "If client agrees"
    Required = "Required"


class TaskStatus:
    """
    Gateway task status

    :ivar str Failed: The task has failed
    :ivar str Running: The task is running
    :ivar str Completed: The task has completed
    """
    Failed = "failed"
    Running = "running"
    Completed = "completed"


class TCPConnectRC:
    Open = "Open"


class License:
    """
    Gateway license types

    :ivar str EV4: EV4 license
    :ivar str EV8: EV8 license
    :ivar str EV16: EV16 license
    :ivar str EV32: EV32 license
    :ivar str EV64: EV64 license
    :ivar str EV128: EV128 license
    """
    EV4 = "EV4"
    EV8 = "EV8"
    EV16 = "EV16"
    EV32 = "EV32"
    EV64 = "EV64"
    EV128 = "EV128"


class OperationMode:
    """
    Gateway operation mode

    :ivar str Disabled: Gateway is Disabled
    :ivar str CachingGateway: Gateway is in Caching mode
    """
    Disabled = "Disabled"
    CachingGateway = "CachingGateway"


class Acl:
    """
    ACL types

    :ivar str WindowsNT: Windows NT ACL Mode
    :ivar str OnlyAuthenticatedUsers: Authenticated Users ACL Mode
    """
    WindowsNT = "winAclMode"
    OnlyAuthenticatedUsers = "authenticated"


class ClientSideCaching:
    """
    Client side caching types

    :ivar str Manual: Manual client side caching
    :ivar str Documents: Documents client side caching
    :ivar str Disabled: Client side caching disabled
    """
    Manual = "manual"
    Documents = "documents"
    Disabled = "disabled"


class PrincipalType:
    """
    ACL Principal Type

    :ivar str LU: Local User
    :ivar str LG: Local Group
    :ivar str DU: Domain User
    :ivar str DG: Domain Group
    """
    LU = "LocalUser"
    LG = "LocalGroup"
    DU = "DomainUser"
    DG = "DomainGroup"


class LocalGroup:
    """
    Local Group types

    :ivar str Administrators: Administrators
    :ivar str ReadOnlyAdministrators: Read Only Administrators
    :ivar str Everyone: Everyone

    """
    Administrators = "Administrators"
    ReadOnlyAdministrators = "Read Only Administrators"
    Everyone = "Everyone"


class FileAccessMode:
    """
    File Access Mode

    :ivar str RW: Read Write
    :ivar str RO: Read Only
    :ivar str NA: None
    """
    RW = "ReadWrite"
    RO = "ReadOnly"
    NA = "None"


class SyncStatus:
    """
    Gateway sync status

    :ivar str Off: Off
    :ivar str NotInitialized: Not Initialized
    :ivar str InitializingConnection: Initializing Connection
    :ivar str ConnectingFolders: Connecting Folders
    :ivar str Connected: Connected
    :ivar str ClocksOutOfSync: Clocks is Out Of Sync
    :ivar str ConnectionFailed: Connection Failed
    :ivar str InternalError: Internal Error
    :ivar str InvalidConfiguration: Invalid Configuration
    :ivar str VolumeUnavailable: Volume Unavailable
    :ivar str NoFolder: No Folder
    :ivar str DisconnectedPortal: Disconnected from Portal
    :ivar str ServiceUnavailable: Service is Unavailable
    :ivar str Unlicensed: Unlicensed
    :ivar str Synced: Synced
    :ivar str Syncing: Syncing
    :ivar str Scanning: Scanning
    :ivar str UpgradingDataBase: Upgrading Database
    :ivar str OutOfQuota: Out of Quota
    :ivar str RejectedByPolicy: Rejected by Policy
    :ivar str FailedFilesInReadOnlyFolder: Failed Files in Read Only Folder
    :ivar str ShouldSupportWinNtAcl: Should Support WinNt Acl
    :ivar str TakingSnapshot: Taking Snapshot
    :ivar str CatalogReadOnlyMode: Catalog ReadOnly Mode
    :ivar str InvalidAverageBlockSize: Invalid Average Block Size
    """
    Off = "Off"
    NotInitialized = "NotInitialized"
    InitializingConnection = "InitializingConnection"
    ConnectingFolders = "ConnectingFolders"
    Connected = "Connected"
    ClocksOutOfSync = "ClocksOutOfSync"
    ConnectionFailed = "ConnectionFailed"
    InternalError = "InternalError"
    InvalidConfiguration = "InvalidConfiguration"
    VolumeUnavailable = "VolumeUnavailable"
    NoFolder = "NoFolder"
    DisconnectedPortal = "DisconnectedPortal"
    ServiceUnavailable = "ServiceUnavailable"
    Unlicensed = "Unlicensed"
    Synced = "Synced"
    Syncing = "Syncing"
    Scanning = "Scanning"
    UpgradingDataBase = "UpgradingDataBase"
    OutOfQuota = "OutOfQuota"
    RejectedByPolicy = "RejectedByPolicy"
    FailedFilesInReadOnlyFolder = "FailedFilesInReadOnlyFolder"
    ShouldSupportWinNtAcl = "ShouldSupportWinNtAcl"
    TakingSnapshot = "TakingSnapshot"
    CatalogReadOnlyMode = "CatalogReadOnlyMode"
    InvalidAverageBlockSize = "InvalidAverageBlockSize"


class AuditEvents:
    """
    Audit log event types

    :ivar str ListFolderReadData: List Folder Read Data
    :ivar str CreateFilesWriteData: Create Files Write Data
    :ivar str CreateFoldersAppendData: Create Folders Append Data
    :ivar str ReadExtendedAttributes: Read Extended Attributes
    :ivar str WriteExtendedAttributes: Write Extended Attributes
    :ivar str TraverseFolderExecuteFile: Traverse Folder Execute File
    :ivar str DeleteSubfoldersAndFiles: Delete Subfolders And Files
    :ivar str WriteAttributes: Write Attributes
    :ivar str Delete: Delete
    :ivar str ChangePermissions: Change Permissions
    :ivar str ChangeOwner: Change Owner
    """
    ListFolderReadData = "RD"
    CreateFilesWriteData = "WD"
    CreateFoldersAppendData = "AD"
    ReadExtendedAttributes = "REA"
    WriteExtendedAttributes = "WEA"
    TraverseFolderExecuteFile = "X"
    DeleteSubfoldersAndFiles = "DC"
    WriteAttributes = "WA"
    Delete = "DE"
    ChangePermissions = "WDAC"
    ChangeOwner = "WO"


class ServicesConnectionState:
    """
    Gateway connection status

    :ivar str Disconnected: The Gateway is disconnected from CTERA Portal
    :ivar str Connected: The Gateway is connected to CTERA Portal
    """
    Disconnected = "Disconnected"
    Connected = "Connected"


class RAIDLevel:
    """
    RAID Levels

    :ivar str JBOD: Linear concatenation
    :ivar str RAID_0: Stripe set
    :ivar str RAID_1: Mirror
    :ivar str RAID_5: Distributed parity
    :ivar str RAID_6: Dual parity
    """
    JBOD = "linear"
    RAID_0 = "0"
    RAID_1 = "1"
    RAID_5 = "5"
    RAID_6 = "6"


class BackupConfStatusID:
    """
    Status of backup configuration

    :ivar str NotInitialized: Backup configuration was not initialized
    :ivar str Configuring: Backup is being configured
    :ivar str Attaching: Backup configuration is Attaching
    :ivar str Attached: Backup configuration is Attached
    :ivar str NoFolder: No Folder for backup
    :ivar str WrongPassword: Wrong password used
    :ivar str Failed: Backup configuration failed
    :ivar str Unsubscribed: Unsubscribed to backup
    :ivar str Unlicensed: Unlicensed" to backup
    :ivar str ClocksOutOfSync: Clocks are out of sync
    :ivar str GetFoldersList: Get folders list
    """
    NotInitialized = "NotInitialized"
    Configuring = "Configuring"
    Attaching = "Attaching"
    Attached = "Attached"
    NoFolder = "NoFolder"
    WrongPassword = "WrongPassword"
    Failed = "Failed"
    Unsubscribed = "Unsubscribed"
    Unlicensed = "Unlicensed"
    ClocksOutOfSync = "ClocksOutOfSync"
    GetFoldersList = "GetFoldersList"
