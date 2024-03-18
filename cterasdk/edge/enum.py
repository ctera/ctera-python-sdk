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
    Edge Filer volume status

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
    Edge Filer task status

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
    Edge Filer license types

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
    Edge Filer operation mode

    :ivar str Disabled: Edge Filer is Disabled
    :ivar str CachingGateway: Edge Filer is in Caching mode
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
    Disabled = "disable"


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
    Edge Filer sync status

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
    Edge Filer connection status

    :ivar str ResolvingServers: The Edge Filer is resolving CTERA Portal servers
    :ivar str Connecting: The Edge Filer is in connecting to CTERA Portal
    :ivar str Attaching: The Edge Filer is attaching to CTERA Portal
    :ivar str Authenticating: The Edge Filer is authenticating to CTERA Portal
    :ivar str Disconnected: The Edge Filer is disconnected from CTERA Portal
    :ivar str Connected: The Edge Filer is connected to CTERA Portal
    """
    ResolvingServers = "ResolvingServers"
    Connecting = "Connecting"
    Attaching = "Attaching"
    Authenticating = "Authenticating"
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
    LVM = 'LVM'


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


class Traffic:
    """
    Traffic type

    :ivar str Upload: Upload
    :ivar str Download: Download
    """
    Upload = 'Upload'
    Download = 'Download'


class SMBProtocol:
    """
    SMB Protocol

    :ivar str SMB1: SMB v1
    :ivar str NT1: SMB v1
    :ivar str SMB2_02: Vista, Server 2008
    :ivar str SMB2_10: Windows 7, Server 2008 R2
    :ivar str SMB3_00: Windows 8, Server 2012
    :ivar str SMB3_02: Windows 8.1, Server 2012 R2
    :ivar str SMB3_11: Windows 10, Server 2016
    :ivar str SMB2: Windows 7, Server 2008
    :ivar str SMB3: SMB 3.1.1
    """
    SMB1 = 'NT1'
    NT1 = SMB1
    SMB2_02 = 'SMB2_02'
    SMB2_10 = 'SMB2_10'
    SMB3_00 = 'SMB3_00'
    SMB3_02 = 'SMB3_02'
    SMB3_11 = 'SMB3_11'
    SMB2 = 'SMB2'
    SMB3 = 'SMB3'


class SourceType:
    """
    Source Host Type

    :ivar str Edge: This Edge Filer
    :ivar str Windows: Windows Server
    :ivar str ONTAP: NetApp ONTAP
    :ivar str OneFS: Isilon OneFS
    :ivar str Panzura: Panzura Freedom Filer
    :ivar str SGRID9_SMB: NetApp StorageGRID 9
    :ivar str SGRID11_SMB: NetApp StorageGRID 11
    :ivar str StorSimple: Microsoft Azure StorSimple
    """
    Edge = 'currentDevice'
    Windows = 'windowsServer'
    ONTAP = 'netapp'
    OneFS = 'isilon'
    Panzura = 'panzura'
    SGRID9_SMB = 'storageGrid9'
    SGRID11_SMB = 'storageGrid11'
    StorSimple = 'azureStorSimple'


class TaskType:
    """
    Migration Tool Task Type

    :ivar str Discovery: Discovery
    :ivar str Migration: Migration
    """
    Discovery = 0
    Migration = 1
