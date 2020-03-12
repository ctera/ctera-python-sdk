from cterasdk.edge import volumes
from tests.ut import base_edge


class TestEdgeVolumes(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._volume_name = 'localcache'

    def test_get_all_volumes(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = volumes.Volumes(self._filer).get()
        self._filer.get.assert_called_once_with('/config/storage/volumes')
        self.assertEqual(ret, get_response)

    def test_get_volume(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = volumes.Volumes(self._filer).get(self._volume_name)
        self._filer.get.assert_called_once_with('/config/storage/volumes/' + self._volume_name)
        self.assertEqual(ret, get_response)
