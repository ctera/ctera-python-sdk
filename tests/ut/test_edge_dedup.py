from unittest import mock

from cterasdk.edge import dedup
from tests.ut import base_edge


class TestEdgeDedup(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._size = 5
        self._usage = 6
        self._mock_reboot = self.patch_call('cterasdk.edge.power.reboot')

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
        ret = dedup.Dedup(self._filer).enable(reboot=True, wait=True)
        self._filer.api.put.assert_called_once_with('/config/dedup/useLocalMapFileDedup', False)
        self._mock_reboot.assert_not_called
        self.assertEqual(ret, put_response)

    def test_status(self):
        self._init_filer()
        self._filer.api.execute = mock.MagicMock(side_effect=self._execute_side_effect)
        ret = dedup.Dedup(self._filer).status()
        self._filer.api.execute.assert_has_calls([
            mock.call('/config/cloudsync/cloudExtender', 'allFilesTotalUsedBytes'),
            mock.call('/config/cloudsync/cloudExtender', 'storageUsedBytes')
        ])
        self.assertEqual(ret.size, self._size)
        self.assertEqual(ret.usage, self._usage)

    def _execute_side_effect(self, path, name, param):
        # pylint: disable=unused-argument
        if name == 'allFilesTotalUsedBytes':
            return self._size
        if name == 'allFilesTotalUsedBytes':
            return self._usage

    def test_run_regenerate(self):
        execute_response = 'Success'
        self._init_filer(execute_response=execute_response)
        ret = dedup.Dedup(self._filer).regen.run()
        self._filer.api.execute.assert_called_once_with('/config/dedup', 'regenerate', mock.ANY)
        self.assertEqual(ret, execute_response)

    def test_regen_status(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = dedup.Dedup(self._filer).regen.run()
        self._filer.api.get.assert_called_once_with('/proc/dedup/regenerate/general')
        self.assertEqual(ret, get_response)
    