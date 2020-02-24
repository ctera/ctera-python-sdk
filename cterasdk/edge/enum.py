class Mode:
    Enabled = "enabled"
    Disabled = "disabled"


class IPProtocol:
    TCP = "TCP"
    UDP = "UDP"


class Severity:
    EMERGENCY = "emergency"
    ALERT = "alert"
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"
    INFO = "info"
    DEBUG = "debug"


class VolumeStatus:
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
    Disabled = "Disabled"
    IfClientAgrees = "If client agrees"
    Required = "Required"


class TaskStatus:
    Failed = "failed"
    Running = "running"
    Completed = "completed"


class TCPConnectRC:
    Open = "Open"


class License:
    EV4 = "EV4"
    EV8 = "EV8"
    EV16 = "EV16"
    EV32 = "EV32"
    EV64 = "EV64"
    EV128 = "EV128"


class OperationMode:
    Disabled = "Disabled"
    CachingGateway = "CachingGateway"


class Acl:
    WindowsNT = "winAclMode"
    OnlyAuthenticatedUsers = "authenticated"


class ClientSideCaching:
    Manual = "manual"
    Documents = "documents"
    Disabled = "disabled"


class PrincipalType:
    LU = "LocalUser"
    LG = "LocalGroup"
    DU = "DomainUser"
    DG = "DomainGroup"


class LocalGroup:
    Administrators = "Administrators"
    ReadOnlyAdministrators = "Read Only Administrators"
    Everyone = "Everyone"


class FileAccessMode:
    RW = "ReadWrite"
    RO = "ReadOnly"
    NA = "None"


class SyncStatus:
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
