from .enum import Mode
from ..common import Object


def enable(ctera_host, path, auditEvents, logKeepPeriod, maxLogKBSize, maxRotateTime, includeAuditLogTag, humanReadableAuditLog):
    settings = Object()
    settings.mode = Mode.Enabled
    settings.path = path
    settings.auditEvents = auditEvents
    settings.logKeepPeriod = logKeepPeriod
    settings.maxLogKBSize = maxLogKBSize
    settings.maxRotateTime = maxRotateTime
    settings.includeAuditLogTag = includeAuditLogTag
    settings.humanReadableAuditLog = humanReadableAuditLog

    ctera_host.put('/config/logging/files', settings)


def disable(ctera_host):
    ctera_host.put('/config/logging/files/mode', Mode.Disabled)
