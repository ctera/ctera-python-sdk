from unittest import mock

from cterasdk.edge import statistics
from cterasdk.edge.enum import Interval, Metric
from tests.ut.edge import base_edge


class TestEdgeStatistics(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._filer.stats.get = mock.MagicMock()
        self.intervals = (Interval.Hour, Interval.Day, Interval.Week, Interval.Month, Interval.Year)

    def test_cpu(self):
        for interval in self.intervals:
            self._init_filer()
            statistics.Statistics(self._filer).cpu(interval)
            self._filer.stats.get.assert_called_with(Metric.CPU, params={'interval': interval})

    def test_memory(self):
        self._init_filer()
        for interval in self.intervals:
            self._init_filer()
            statistics.Statistics(self._filer).memory(interval)
            self._filer.stats.get.assert_called_with(Metric.Memory, params={'interval': interval})

    def test_volume(self):
        for interval in self.intervals:
            self._init_filer()
            statistics.Statistics(self._filer).volume(interval)
            self._filer.stats.get.assert_called_with(Metric.Volume, params={'interval': interval})

    def test_cache(self):
        for interval in self.intervals:
            self._init_filer()
            statistics.Statistics(self._filer).cache(interval)
            self._filer.stats.get.assert_called_with(Metric.Cache, params={'interval': interval})

    def test_connections(self):
        for interval in self.intervals:
            self._init_filer()
            statistics.Statistics(self._filer).connections(interval)
            self._filer.stats.get.assert_called_with(Metric.Connections, params={'interval': interval})

    def test_disk(self):
        for interval in self.intervals:
            self._init_filer()
            statistics.Statistics(self._filer).disk(interval)
            self._filer.stats.get.assert_called_with(Metric.Disk, params={'interval': interval})

    def test_local_io(self):
        for interval in self.intervals:
            self._init_filer()
            statistics.Statistics(self._filer).local_io(interval)
            self._filer.stats.get.assert_called_with(Metric.Local, params={'interval': interval})

    def test_cloudsync(self):
        for interval in self.intervals:
            self._init_filer()
            statistics.Statistics(self._filer).cloudsync(interval)
            self._filer.stats.get.assert_called_with(Metric.CloudSync, params={'interval': interval})
