from unittest import mock

from cterasdk.edge import dedup
from tests.ut.edge import base_edge


class TestEdgeDedup(base_edge.BaseEdgeTest):

    Size = 2
    Usage = 1

    def setUp(self):
        super().setUp()
        self._mock_reboot = self.patch_call('cterasdk.edge.power.Power.reboot')

    def test_is_enabled(self):
        get_response = True
        self._init_filer(get_response=get_response)
        ret = dedup.Dedup(self._filer).is_enabled()
        self._filer.api.get.assert_called_once_with('/config/dedup/useLocalMapFileDedup')
        self.assertEqual(ret, True)

    def test_enable_reboot_wait(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ret = dedup.Dedup(self._filer).enable(reboot=True, wait=True)
        self._filer.api.put.assert_called_once_with('/config/dedup/useLocalMapFileDedup', True)
        self._mock_reboot.assert_called_once_with(True)
        self.assertEqual(ret, put_response)

    def test_disable_no_reboot(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ret = dedup.Dedup(self._filer).disable(reboot=False, wait=True)
        self._filer.api.put.assert_called_once_with('/config/dedup/useLocalMapFileDedup', False)
        self._mock_reboot.assert_not_called()
        self.assertEqual(ret, put_response)

    def test_status(self):
        self._init_filer()
        self._filer.api.execute = mock.MagicMock(side_effect=self._execute_side_effect)
        ret = dedup.Dedup(self._filer).status()
        self._filer.api.get.assert_called_once_with('/config/dedup/useLocalMapFileDedup')
        self._filer.api.execute.assert_has_calls([
            mock.call('/config/cloudsync/cloudExtender', 'allFilesTotalUsedBytes'),
            mock.call('/config/cloudsync/cloudExtender', 'storageUsedBytes')
        ])
        self.assertEqual(ret.size, TestEdgeDedup.Size)
        self.assertEqual(ret.usage, TestEdgeDedup.Usage)

    @staticmethod
    def _execute_side_effect(path, name):
        # pylint: disable=unused-argument
        if name == 'allFilesTotalUsedBytes':
            return TestEdgeDedup.Size
        if name == 'storageUsedBytes':
            return TestEdgeDedup.Usage
        return None

    def test_run_regenerate(self):
        execute_response = 'Success'
        self._init_filer(execute_response=execute_response)
        ret = dedup.Regeneration(self._filer).run()
        self._filer.api.execute.assert_called_once_with('/config/dedup', 'regenerate', mock.ANY)
        self.assertEqual(ret, execute_response)

    def test_regen_status(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = dedup.Regeneration(self._filer).status()
        self._filer.api.get.assert_called_once_with('/proc/dedup/regenerate/general')
        self.assertEqual(ret, get_response)
