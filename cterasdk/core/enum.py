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
