from . import enum
from ..common import Object
from .base_command import BaseCommand


class Audit(BaseCommand):

    defaultAuditEvents = [
        enum.AuditEvents.CreateFilesWriteData,
        enum.AuditEvents.CreateFoldersAppendData,
        enum.AuditEvents.WriteExtendedAttributes,
        enum.AuditEvents.DeleteSubfoldersAndFiles,
        enum.AuditEvents.WriteAttributes,
        enum.AuditEvents.Delete,
        enum.AuditEvents.ChangePermissions,
        enum.AuditEvents.ChangeOwner
    ]

    def enable(
            self,
            path,
            auditEvents=None,
            logKeepPeriod=30,
            maxLogKBSize=102400,
            maxRotateTime=1440,
            includeAuditLogTag=True,
            humanReadableAuditLog=False):
        settings = Object()
        settings.mode = enum.Mode.Enabled
        settings.path = path
        settings.auditEvents = auditEvents or Audit.defaultAuditEvents
        settings.logKeepPeriod = logKeepPeriod
        settings.maxLogKBSize = maxLogKBSize
        settings.maxRotateTime = maxRotateTime
        settings.includeAuditLogTag = includeAuditLogTag
        settings.humanReadableAuditLog = humanReadableAuditLog

        self._gateway.put('/config/logging/files', settings)

    def disable(self):
        self._gateway.put('/config/logging/files/mode', enum.Mode.Disabled)
