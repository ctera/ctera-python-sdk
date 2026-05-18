from cterasdk.edge import stats
from tests.ut.edge import base_edge


class TestEdgeStats(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._init_filer()

    def test_get_cpu_default_interval(self):
        stats.Stats(self._filer).get('cpu')
        self._filer.api.get.assert_called_with('/stats/cpu', params={'interval': 'hour'})

    def test_get_memory_with_interval(self):
        stats.Stats(self._filer).get('memory', interval='day')
        self._filer.api.get.assert_called_with('/stats/memory', params={'interval': 'day'})

    def test_get_all_stat_types(self):
        for stat_type in stats.VALID_STAT_TYPES:
            self._filer.api.get.reset_mock()
            stats.Stats(self._filer).get(stat_type, interval='hour')
            self._filer.api.get.assert_called_with(f'/stats/{stat_type}', params={'interval': 'hour'})

    def test_get_all_intervals(self):
        for interval in stats.VALID_INTERVALS:
            self._filer.api.get.reset_mock()
            stats.Stats(self._filer).get('cpu', interval=interval)
            self._filer.api.get.assert_called_with('/stats/cpu', params={'interval': interval})

    def test_invalid_stat_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            stats.Stats(self._filer).get('invalid_type')

    def test_invalid_interval_raises_value_error(self):
        with self.assertRaises(ValueError):
            stats.Stats(self._filer).get('cpu', interval='invalid_interval')
