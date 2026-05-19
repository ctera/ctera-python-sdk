from cterasdk.edge import statistics
from cterasdk.edge.enum import Interval, Metric
from tests.ut.edge import base_edge


class TestEdgeStatistics(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()

        self.metrics = (
            Metric.CPU,
            Metric.Memory,
            Metric.Volume,
            Metric.Cache,
            Metric.Connections,
            Metric.Disk,
            Metric.Local,
            Metric.CloudSync,
        )

        self.intervals = (
            Interval.Hour,
            Interval.Day,
            Interval.Week,
            Interval.Month,
            Interval.Year,
        )

    def test_statistics(self):
        for metric in self.metrics:
            for interval in self.intervals:
                self._init_filer()

                statistics.Statistics(self._filer)._statistics(metric, interval)

                self._filer.api.get.assert_called_once_with(
                    metric,
                    params={'interval': interval}
                )
