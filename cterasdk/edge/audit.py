from . import enum
from ..common import Object
from .base_command import BaseCommand


class Audit(BaseCommand):
    """
    Gateway Audit configuration APIs

    :ivar list[cterasdk.edge.enum.AuditEvents] defaultAuditEvents: Default audit events
    """

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
        """
        Enable Gateway Audit log

        :param str path: Path to save the audit log
        :param list[cterasdk.edge.enum.AuditEvents],optional auditEvents:
         List of audit event types to save, defaults to Audit.defaultAuditEvents
        :param int,optional logKeepPeriod: Period to key the logs in days, defaults to 30
        :param int,optional maxLogKBSize: The maximum size of the log file in KB, defailts to 102400 (100 MB)
        :param int,optional maxRotateTime: The maximal time before rotating the log file in Minutes, defaults to 1440 (24 hours)
        :param bool,optional includeAuditLogTag: Include audit log tag, defailts to True
        :param bool,optional humanReadableAuditLog: Human readable audit log, defailts to False
        """
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
        """
        Disable Gateway Audit log
        """
        self._gateway.put('/config/logging/files/mode', enum.Mode.Disabled)
