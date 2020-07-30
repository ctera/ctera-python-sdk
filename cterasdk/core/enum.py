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
