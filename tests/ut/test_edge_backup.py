from cterasdk.edge import backup
from tests.ut import base_edge


class TestEdgeBackup(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._task_id = '137'
        self._shared_secret = 'shared secret'
        self._passphrase_salt = 'salt'

    def test_start_backup(self):
        self._init_filer()
        backup.Backup(self._filer).start()
        self._filer.execute.assert_called_once_with('/status/sync', 'start')

    def test_suspend_backup(self):
        self._init_filer()
        backup.Backup(self._filer).suspend()
        self._filer.execute.assert_called_once_with('/status/sync', 'pause')

    def test_unsuspend_backup(self):
        self._init_filer()
        backup.Backup(self._filer).unsuspend()
        self._filer.execute.assert_called_once_with('/status/sync', 'resume')
