class Context:
    """
    Portal connection context

    :ivar str admin: Global admin context
    :ivar str ServicesPortal: Services Portal context
    """
    admin = 'admin'
    ServicesPortal = 'ServicesPortal'


class LogTopic:
    """
    Portal Log Topic

    :ivar str System: System log topic
    :ivar str CloudBackup: Cloud Backup log topic
    :ivar str CloudSync: Cloud Sync log topic
    :ivar str Access: Access log topic
    :ivar str Audit: Audit log topic
    """
    System = 'system'
    CloudBackup = 'backup'
    CloudSync = 'cloudsync'
    Access = 'access'
    Audit = 'audit'


class OriginType:
    """
    Log Origin Type

    :ivar str Portal: Portal originated logs
    :ivar str Device: Device originated logs
    """
    Portal = 'Portal'
    Device = 'Device'


class DeviceType:
    """
    Device type

    :ivar str CloudPlug: Cloud Plug device
    :ivar str C200: C200 device
    :ivar str C400: C400 device
    :ivar str C800: C800 device
    :ivar str C800P: C800P device
    :ivar str vGateway: vGateway device
    :ivar str ServerAgent: Server Agent device
    :ivar str WorkstationAgent: Workstation Agent Agent device
    :ivar list[str] Gateways: List of all the Gateway DeviceTypes
    :ivar list[str] Agents: List of all the Agents DeviceTypes
    """
    CloudPlug = "CloudPlug"
    C200 = "C200"
    C400 = "C400"
    C800 = "C800"
    C800P = "C800P"
    vGateway = "vGateway"
    ServerAgent = "Server Agent"
    WorkstationAgent = "Workstation Agent"
    Gateways = [CloudPlug, C200, C400, C800, C800P, vGateway]
    Agents = [ServerAgent, WorkstationAgent]


class Role:
    """
    Portal User Role

    :ivar str Disabled: Disabled user role
    :ivar str EndUser: EndUser user role
    :ivar str ReadWriteAdmin: ReadWriteAdmin user role
    :ivar str ReadOnlyAdmin: ReadOnlyAdmin user role
    :ivar str Support: Support user role
    """
    Disabled = "Disabled"
    EndUser = "EndUser"
    ReadWriteAdmin = "ReadWriteAdmin"
    ReadOnlyAdmin = "ReadOnlyAdmin"
    Support = "Support"


class RoleResolver:
    """
    Role Settings Resolver

    :ivar str ReadWriteAdmin: ReadWriteAdmin user role
    :ivar str ReadOnlyAdmin: ReadOnlyAdmin user role
    :ivar str Support: Support user role
    """
    ReadWriteAdmin = "readWriteAdminSettings"
    ReadOnlyAdmin = "readOnlyAdminSettings"
    Support = "supportAdminSettings"
    ComplianceOfficer = 'complianceOfficerSettings'


class Severity:
    """
    Portal Log Severity

    :ivar str EMERGENCY: Emergency log severity
    :ivar str ALERT: Alert log severity
    :ivar str CRITICAL: Critical log severity
    :ivar str ERROR: Error log severity
    :ivar str WARNING: Warning log severity
    :ivar str NOTICE: Notice log severity
    :ivar str INFO: Info log severity
    :ivar str DEBUG: Debug log severity
    """
    EMERGENCY = "emergency"
    ALERT = "alert"
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"
    INFO = "info"
    DEBUG = "debug"


class PortalAccountType:
    """
    Portal Account Type

    :ivar str User: User account type
    :ivar str Group: Group account type
    """
    User = "user"
    Group = "group"


class SearchType:
    """
    Search Type

    :ivar str User: User search type
    :ivar str Group: Group search type
    """
    Users = "users"
    Groups = "groups"


class PolicyType:
    """
    Zone Policy Type

    :ivar str ALL: All folders
    :ivar str SELECT: Selected Folders
    :ivar str NONE: No Folders
    """
    ALL = 'allFolders'
    SELECT = 'selectedFolders'
    NONE = 'noFolders'


class ProtectionLevel:
    """
    External Share Protection Level

    :ivar str publicLink: No authentication
    :ivar str email: 2FA via email
    """
    Public = 'publicLink'
    Email = 'email'


class FileAccessMode:
    """
    Share Access Mode

    :ivar str RW: Read Write
    :ivar str RO: Read Only
    :ivar str PO: Preview Only
    :ivar str NA: None
    """
    RW = "ReadWrite"
    RO = "ReadOnly"
    PO = "PreviewOnly"
    NA = "None"


class CollaboratorType:
    """
    Collaborator Type

    :ivar str LU: Local User
    :ivar str DU: Domain User
    :ivar str LG: Local Group
    :ivar str DG: Domain Group
    :ivar str EXT: External
    """
    LU = "localUser"
    LG = "localGroup"
    DU = "adUser"
    DG = "adGroup"
    EXT = "external"


class PortalType:
    """
    Portal Type

    :ivar str Team: Team Portal
    :ivar str Reseller: Reseller Portal
    """
    Team = 'team'
    Reseller = 'reseller'


class ServerMode:
    """
    Portal Server Mode

    :ivar str Master: Master
    :ivar str Slave: Slave
    """
    Master = 'master'
    Slave = 'slave'


class SetupWizardStatus:
    """
    Portal Setup Wizard Status

    :ivar str NA: Not Relevant
    :ivar str Running: In Progress
    :ivar str Failed: Failed
    :ivar str Completed: Completed
    """
    NA = "notRelevant"
    Running = "inProgress"
    Failed = "failed"
    Completed = "completed"


class SetupWizardStage:
    """
    Portal Setup Wizard Stage

    :ivar str Server: Initializing Server
    :ivar str Portal: Initializing Portal
    :ivar str Replication: Setting Database Replication
    :ivar str Restart: Restarting Server
    :ivar str Finish: Finished
    """
    Server = "initServer"
    Portal = "initPortal"
    Replication = "setReplication"
    Restart = "restartingServer"
    Finish = "finish"


class SlaveAuthenticaionMethod:
    """
    Secondary Portal server authentication mode

    :ivar str Password: Password
    :ivar str PrivateKey: Private Key
    """
    Password = 'Password'
    PrivateKey = 'Key'


class PlanRetention:
    """
    Portal plan retention policy

    :ivar str All: All versions
    :ivar str Hourly: Hourly versions
    :ivar str Daily: Daily versions
    :ivar str Weekly: Weekly versions
    :ivar str Monthly: Monthly versions
    :ivar str Quarterly: Quarterly versions
    :ivar str Yearly: Yearly versions
    :ivar str Deleted: Recycle bin
    """
    All = 'retainAll'
    Hourly = 'hourly'
    Daily = 'daily'
    Weekly = 'weekly'
    Monthly = 'monthly'
    Quarterly = 'quarterly'
    Yearly = 'yearly'
    Deleted = 'retainDeleted'


class PlanItem:
    """
    Portal plan item

    :ivar str EV4: EV4
    :ivar str EV8: EV8
    :ivar str EV16: EV16
    :ivar str EV32: EV32
    :ivar str EV64: EV64
    :ivar str EV128: EV128
    :ivar str WA: Workstation Agent
    :ivar str SA: Server Agent
    :ivar str Share: Cloud Drive
    :ivar str Connect: Cloud Drive Connect
    """
    EV4 = 'EV4'
    EV8 = 'EV8'
    EV16 = 'EV16'
    EV32 = 'EV32'
    EV64 = 'EV64'
    EV128 = 'EV128'
    WA = 'WA'
    SA = 'SA'
    Share = 'Share'
    Connect = 'Connect'
    Storage = 'Storage'


class PlanService:
    """
    Plan Service

    :ivar str CloudDrive: Cloud Drive
    :ivar str CloudBackup: Cloud Backup
    :ivar str Seeding: Seeding
    :ivar str Remote: Remote Access
    """
    CloudDrive = 'Cloud folders'
    CloudBackup = 'Cloud Backup'
    Seeding = 'Seeding'
    Remote = 'Remote Access'


class PlanServiceState:
    """
    Plan Service State

    :ivar str Enabled: Enabled
    :ivar str Disabled: Disabled
    :ivar str Connect: Cloud Drive Connect
    """
    Enabled = 'OK'
    Disabled = 'Disabled'
    Connect = 'Lite'


class ListFilter:
    """
    Cloud Drive Folder List Filter

    :ivar str All: All
    :ivar str Deleted: Deleted
    :ivar str NonDeleted: NonDeleted
    """
    All = 'All'
    Deleted = 'Deleted'
    NonDeleted = 'NonDeleted'


class PlanCriteria:
    """
    Subscription Plan Auto Assignment Rule Builder Criterias

    :ivar str Username: Username
    :ivar str Groups: User groups
    :ivar str Role: User role
    :ivar str First: User first name
    :ivar str Last: User last name
    :ivar str Company: User company
    :ivar str BillingId: User billing id
    :ivar str Comment: User comment
    """
    Username = 'username'
    Groups = 'userGroups'
    Role = 'role'
    First = 'firstName'
    Last = 'lastName'
    Company = 'company'
    BillingId = 'billingId'
    Comment = 'comment'


class AntivirusType:
    """
    Antivirus Type

    :ivar str McAfeeWG: McAfee Web Gateway
    :ivar str Symantec: Symantec Protection Engine
    :ivar str ESET: ESET Gateway Security
    :ivar str Sophos: Sophos AV
    :ivar str McAfeeVSES: McAfee VirusScan Enterprise for Storage
    :ivar str TrendMicro: Trend Micro InterScan
    """
    McAfeeWG = 'McAfee'
    Symantec = 'Symantec'
    ESET = 'Eset'
    Sophos = 'Sophos'
    McAfeeVSES = 'McAfeeVSES'
    TrendMicro = 'TrendMicro'


class ICAPServices:
    """
    ICAP Services

    :ivar str Antivirus: Antivirus
    :ivar str DLP: Data Loss Prevention
    """
    Antivirus = "Antivirus"
    DLP = "DLP"


class LocationType:
    """
    Location Type

    :ivar str Azure: Azure Blob Storage
    :ivar str S3: Amazon Web Services S3
    :ivar str S3Compatible: S3 Compatible
    :ivar str NetAppStorageGRID: NetApp StorageGRID WebScale (S3)
    """
    Azure = 'AzureLocation'
    S3 = 'S3Location'
    S3Compatible = 'S3Compatible'
    NetAppStorageGRID = 'NetAppLocation'


class BucketType:
    """
    Bucket Type

    :ivar str Azure: Azure
    :ivar str Scality: Scality
    :ivar str AWS: Amazon Web Services S3
    :ivar str ICOS: IBM Cloud Object Storage
    :ivar str GenericS3: Generic S3
    :ivar str Nutanix: Nutanix S3
    :ivar str Wasabi: Wasabi S3
    :ivar str Google: Google S3
    :ivar str NetAppStorageGRID: NetApp StorageGRID WebScale (S3)
    """
    Azure = 'Azure'
    Scality = 'ScalityS3'
    AWS = 'S3'
    ICOS = 'CleverSafeS3'
    GenericS3 = 'GenericS3'
    Nutanix = 'Nutanix'
    Wasabi = 'WasabiS3'
    Google = 'GoogleS3'
    NetAppStorageGRID = 'NTAP'


class EnvironmentVariables:
    """
    Environment Variables.\n
    Some environment variables are applicable across platforms (i.e. Windows, Linux), while others are limited to a designated platform

    :ivar str ALLUSERSPROFILE: All users profile
    :ivar str WINDIR: Windows directory
    :ivar str TEMP: Temp directory
    :ivar str SYSTEMDRIVE: System drive
    :ivar str PROGRAMFILES: Program files
    :ivar str APPDATA: Application data
    :ivar str USERPROFILE: Current user profile
    :ivar str PRIMARYUSER: Primary user
    :ivar str USERS: Users directory (CTERA Edge Filer)
    :ivar str AGENTS: Agents directory (CTERA Edge Filer)
    :ivar str SYNCS: Syncs directory (CTERA Edge Filer)
    :ivar str PROJECTS: Projects directory (CTERA Edge Filer)
    """
    ALLUSERSPROFILE = '$ALLUSERSPROFILE'
    WINDIR = '$WINDIR'
    TEMP = '$TEMP'
    SYSTEMDRIVE = '$SYSTEMDRIVE'
    PROGRAMFILES = '$PROGRAMFILES'
    APPDATA = '$APPDATA'
    USERPROFILE = '$USERPROFILE'
    USERS = '$USERS'
    AGENTS = '$AGENTS'
    SYNCS = '$SYNCS'
    PROJECTS = '$PROJECTS'
    PRIMARYUSER = '$PRIMARYUSER'


class Platform:
    """
    CTERA Edge Platform Type.\n

    :ivar str C200_Orion: All users profile
    :ivar str C200_ARM: Windows directory
    :ivar str C200_Kirkwood: Temp directory
    :ivar str C400_C800: System drive
    :ivar str Edge_6: CTERA 6.0 Edge Filer
    :ivar str Edge_7: CTERA 7.0 Edge Filer
    :ivar str Windows: Windows Agent (Drive App)
    :ivar str Linux: Linux Agent (Drive App)
    :ivar str OSX: Mac Agent (Drive App)
    """
    C200_Orion = 'Orion'
    C200_ARM = 'ARM'
    C200_Kirkwood = 'Kirkwood'
    C400_C800 = 'X86'
    Edge_6 = 'VBox'
    Edge_7 = 'Genesis'
    Linux = 'LinuxX86'
    Windows = 'WindowsX86'
    OSX = 'OSxX86'


class TemplateCriteria:
    """
    Configuration Template Auto Assignment Rule Builder Criterias

    :ivar str Type: Device type
    :ivar str OperatingSystem: Operating system
    :ivar str Version: Installed software version
    :ivar str Hostname: Hostname
    :ivar str Name: Device name
    :ivar str Owner: Device owner username
    :ivar str Plan: Plan name
    :ivar str Groups: Device owner local or domain groups
    """
    Type = 'DeviceType'
    OperatingSystem = 'OperatingSystem'
    Version = 'InstalledSoftwareVersion'
    Hostname = 'Hostname'
    Name = 'DeviceName'
    Owner = 'OwnerUsername'
    Plan = 'Plan'
    Groups = 'ownerGroups'


class IPProtocol:
    """
    IP Protocol

    :ivar str TCP: TCP Protocol
    :ivar str UDP: UDP Protocol
    """
    TCP = "TCP"
    UDP = "UDP"


class Mode:
    """
    Enum for operational mode

    :ivar str Enabled: Operational mode enabled
    :ivar str Disabled: Operational mode diabled
    """
    Enabled = "enabled"
    Disabled = "disabled"


class DirectoryServiceType:
    """
    Directory Service Type

    :ivar str Microsoft: Active Directory
    :ivar str LDAP: LDAP
    :ivar str Apple: Apple Open Directory
    """
    Microsoft = 'ActiveDirectory'
    LDAP = 'LDAP'
    Apple = 'AppleOpenDirectory'


class DirectoryServiceFetchMode:
    """
    Directory Service Fetch Mode

    :ivar str Eager: Eager
    :ivar str Lazy: Lazy
    """
    Eager = 'Eager'
    Lazy = 'Lazy'


class DirectorySearchEntityType:
    """
    Directory Search Entity Type

    :ivar str User: User
    :ivar str Group: Group
    """
    User = 'user'
    Group = 'group'


class DeduplicationMethodType:
    """
    Folder Group Deduplication Method Type

    :ivar str AverageBlockSize: AverageBlockSize
    :ivar str FixedBlockSize: FixedBlockSize
    """
    AverageBlockSize = 'AverageBlockSize'
    FixedBlockSize = 'FixedBlockSize'


class RetentionMode:
    """
    Write Once Read Many Retention Mode

    :ivar str Enterprise: Enterprise
    :ivar str Compliance: Compliance
    :ivar str Delete: Delete
    """
    Delete = 'None'
    Enterprise = 'Enterprise'
    Compliance = 'Compliance'


class ExtendedAttributes:
    """
    Extended Attributes

    :ivar str MacOS: MacOS
    """
    MacOS = 'MacOS'


class Duration:
    """
    Duration

    :ivar str Minutes: Minutes
    :ivar str Hours: Hours
    :ivar str Days: Days
    :ivar str Months: Months
    :ivar str Years: Years
    """
    Minutes = 'Minutes'
    Hours = 'Hours'
    Days = 'Days'
    Months = 'Months'
    Years = 'Years'


class Reports:
    """
    Reports

    :ivar str Storage: Minutes
    :ivar str Portals: Hours
    :ivar str Folders: Days
    :ivar str FolderGroups: Months
    """
    Storage = 'storageLocationsStatisticsReport'
    Portals = 'portalsStatisticsReport'
    Folders = 'foldersStatisticsReport'
    FolderGroups = 'folderGroupsStatisticsReport'
