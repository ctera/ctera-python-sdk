class Context:
    admin = 'admin'
    ServicesPortal = 'ServicesPortal'


class LogTopic:
    System = 'system'
    CloudBackup = 'backup'
    CloudSync = 'cloudsync'
    Access = 'access'
    Audit = 'audit'


class OriginType:
    Portal = 'Portal'
    Device = 'Device'


class DeviceType:
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
    Disabled = "Disabled"
    EndUser = "EndUser"
    ReadWriteAdmin = "ReadWriteAdmin"
    ReadOnlyAdmin = "ReadOnlyAdmin"
    Support = "Support"


class Severity:
    EMERGENCY = "emergency"
    ALERT = "alert"
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    NOTICE = "notice"
    INFO = "info"
    DEBUG = "debug"


class ActiveDirectoryAccountType:
    User = "user"
    Group = "group"


class SearchType:
    Users = "users"
    Groups = "groups"
