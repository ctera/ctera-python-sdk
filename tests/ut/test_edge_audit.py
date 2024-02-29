from unittest import mock

from cterasdk.edge import audit
from cterasdk.edge.enum import Mode
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeAudit(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._path = '/shared/audit'

    def test_enable_smb_audit_log_default_params(self):
        self._init_filer()
        audit.Audit(self._filer).enable(self._path)
        self._filer.api.put.assert_called_once_with('/config/logging/files', mock.ANY)
        expected_param = TestEdgeAudit._get_smb_audit_log_settings_param(self._path)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_smb_audit_log_settings_param(
            path,
            audit_events=None,
            log_keep_period=30,
            max_log_kb_size=102400,
            max_rotate_time=1440,
            include_audit_log_tag=True,
            human_readable_audit_log=False):
        settings = Object()
        settings.mode = Mode.Enabled
        settings.path = path
        settings.auditEvents = audit_events or audit.Audit.defaultAuditEvents
        settings.logKeepPeriod = log_keep_period
        settings.maxLogKBSize = max_log_kb_size
        settings.maxRotateTime = max_rotate_time
        settings.includeAuditLogTag = include_audit_log_tag
        settings.humanReadableAuditLog = human_readable_audit_log
        return settings

    def test_disable_smb_audit_log(self):
        self._init_filer()
        audit.Audit(self._filer).disable()
        self._filer.api.put.assert_called_once_with('/config/logging/files/mode', Mode.Disabled)
