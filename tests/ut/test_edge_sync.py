from unittest import mock

from cterasdk.edge import sync
from cterasdk.edge.enum import Mode, SyncStatus, Acl
from cterasdk.lib import ErrorStatus
from cterasdk.common.types import ThrottlingRuleBuilder, TimeRange
from tests.ut import base_edge


class TestEdgeSync(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._disable_aio = (False, 0, 0)
        self._enable_aio = (True, 1, 1)
        self._throttling_rule = TestEdgeSync._create_bandwidth_rule(100, 100, '00:00:00', '23:59:59', [0, 1, 2, 3, 4, 5, 6])

    def test_cloudsync_status(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = sync.Sync(self._filer).get_status()
        self._filer.get.assert_called_once_with('/proc/cloudsync/serviceStatus')
        self.assertEqual(ret, get_response)

    def test_is_cloudsync_disabled_when_disbaled(self):
        get_response = Mode.Disabled
        self._init_filer(get_response=get_response)
        ret = sync.Sync(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/cloudsync/mode')
        self.assertEqual(ret, True)

    def test_is_cloudsync_disabled_when_enabled(self):
        get_response = Mode.Enabled
        self._init_filer(get_response=get_response)
        ret = sync.Sync(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/cloudsync/mode')
        self.assertEqual(ret, False)

    def test_is_cloudsync_enabled_when_enabled(self):
        get_response = Mode.Enabled
        self._init_filer(get_response=get_response)
        ret = sync.Sync(self._filer).is_enabled()
        self._filer.get.assert_called_once_with('/config/cloudsync/mode')
        self.assertEqual(ret, True)

    def test_is_cloudsync_enabled_when_disabled(self):
        get_response = Mode.Disabled
        self._init_filer(get_response=get_response)
        ret = sync.Sync(self._filer).is_enabled()
        self._filer.get.assert_called_once_with('/config/cloudsync/mode')
        self.assertEqual(ret, False)

    def test_suspend_cloudsync(self):
        self._init_filer()
        sync.Sync(self._filer).suspend(wait=False)
        self._filer.put.assert_called_once_with('/config/cloudsync/mode', Mode.Disabled)

    def test_unsuspend_cloudsync(self):
        self._init_filer()
        self.patch_call("cterasdk.edge.sync.track")
        sync.Sync(self._filer).unsuspend()
        self._filer.put.assert_called_once_with('/config/cloudsync/mode', Mode.Enabled)

    def test_unsuspend_cloudsync_should_support_winacls(self):
        self._init_filer()
        sync_status_tracker_mock = self.patch_call("cterasdk.edge.sync.track")
        sync_status_tracker_mock.side_effect = ErrorStatus(SyncStatus.ShouldSupportWinNtAcl)
        sync.Sync(self._filer).unsuspend()
        self._filer.put.assert_has_calls(
            [
                mock.call('/config/cloudsync/mode', Mode.Enabled),
                mock.call('/config/fileservices/share/cloud/access', Acl.WindowsNT)
            ]
        )

    def test_unsuspend_cloudsync_error(self):
        self._init_filer()
        sync_status_tracker_mock = self.patch_call("cterasdk.edge.sync.track")
        sync_status_tracker_mock.side_effect = ErrorStatus(SyncStatus.InternalError)
        sync.Sync(self._filer).unsuspend()
        self._filer.put.assert_called_once_with('/config/cloudsync/mode', Mode.Enabled)

    def test_refresh_cloud_drive_folders(self):
        self._init_filer()
        sync.Sync(self._filer).refresh()
        self._filer.execute.assert_called_once_with('/config/cloudsync/cloudExtender', 'refreshPaths', None)

    def test_get_bandwidth_throttling(self):
        get_response = [
            self._throttling_rule.to_server_object()
        ]
        self._init_filer(get_response=get_response)
        ret = sync.CloudSyncBandwidthThrottling(self._filer).get_policy()
        self._filer.get.assert_called_once_with('/config/cloudsync/syncThrottlingTopic/multiThrottling')
        self._assert_equal_objects(ret, [self._throttling_rule])

    def test_set_bandwidth_throttling(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ret = sync.CloudSyncBandwidthThrottling(self._filer).set_policy([self._throttling_rule])
        self._filer.put.assert_called_once_with('/config/cloudsync/syncThrottlingTopic/multiThrottling', mock.ANY)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, [self._throttling_rule.to_server_object()])
        self.assertEqual(ret, put_response)

    def test_print_bandwidth_throttling_rule(self):
        print(self._throttling_rule)

    @staticmethod
    def _create_bandwidth_rule(upload, download, start, end, days):
        schedule = TimeRange().start(start).end(end).days(days).build()
        return ThrottlingRuleBuilder().upload(upload).download(download).schedule(schedule).build()
