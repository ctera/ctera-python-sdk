import logging

from . import enum
from ..common import Object
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Audit(BaseCommand):
    """
    Edge Filer Audit configuration APIs

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
        Enable Edge Filer Audit log

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

        logger.info('Enabling SMB audit logs')
        self._edge.api.put('/config/logging/files', settings)
        logger.info('Audit logs enabled')

    def disable(self):
        """
        Disable Edge Filer Audit log
        """
        logger.info('Disabling SMB audit logs')
        self._edge.api.put('/config/logging/files/mode', enum.Mode.Disabled)
        logger.info('Audit logs disabled')
