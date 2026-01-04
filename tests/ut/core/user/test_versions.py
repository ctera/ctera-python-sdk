import munch
from datetime import datetime
from tests.ut.core.user import base_user


class BaseCoreServicesFilesVersions(base_user.BaseCoreServicesTest):

    def test_list_versions(self):
        directory = 'My Files'
        self._init_services(execute_response=[self._create_snapshot_response(directory, True)])
        ret = self._services.files.versions(directory)
        self._services.api.execute.assert_called_once_with('', 'listSnapshots', f'{self._base}/{directory}')
        self.assertEqual(str(ret[0].path), directory)

    def _create_snapshot_response(self, path, current):
        return munch.Munch({
            'url': self._base,
            'path': path,
            'current': current,
            'startTimestamp': datetime.now().isoformat(),
            'calculatedTimestamp': datetime.now().isoformat()
        })
