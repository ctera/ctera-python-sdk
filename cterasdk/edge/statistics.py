from .enum import Metric
from .base_command import BaseCommand


class Statistics(BaseCommand):
    """ Edge Filer Statistics API """

    def cpu(self, interval):
        """
        CPU Statistics

        :param cterasdk.edge.enum.Interval interval: Interval
        :return: Statistics Object
        :rtype: cterasdk.common.object.Object
        """
        return self._statistics(Metric.CPU, interval)

    def memory(self, interval):
        """
        Memory Statistics

        :param cterasdk.edge.enum.Interval interval: Interval
        :return: Statistics Object
        :rtype: cterasdk.common.object.Object
        """
        return self._statistics(Metric.Memory, interval)

    def volume(self, interval):
        """
        Volume Statistics

        :param cterasdk.edge.enum.Interval interval: Interval
        :return: Statistics Object
        :rtype: cterasdk.common.object.Object
        """
        return self._statistics(Metric.Volume, interval)

    def cache(self, interval):
        """
        Cache Statistics

        :param cterasdk.edge.enum.Interval interval: Interval
        :return: Statistics Object
        :rtype: cterasdk.common.object.Object
        """
        return self._statistics(Metric.Cache, interval)

    def connections(self, interval):
        """
        Connections Statistics

        :param cterasdk.edge.enum.Interval interval: Interval
        :return: Statistics Object
        :rtype: cterasdk.common.object.Object
        """
        return self._statistics(Metric.Connections, interval)

    def disk(self, interval):
        """
        Disk I/O Statistics

        :param cterasdk.edge.enum.Interval interval: Interval
        :return: Statistics Object
        :rtype: cterasdk.common.object.Object
        """
        return self._statistics(Metric.Disk, interval)

    def local_io(self, interval):
        """
        Local I/O Statistics

        :param cterasdk.edge.enum.Interval interval: Interval
        :return: Statistics Object
        :rtype: cterasdk.common.object.Object
        """
        return self._statistics(Metric.Local, interval)

    def cloudsync(self, interval):
        """
        Cloud Synchronization Statistics

        :param cterasdk.edge.enum.Interval interval: Interval
        :return: Statistics Object
        :rtype: cterasdk.common.object.Object
        """
        return self._statistics(Metric.CloudSync, interval)

    def _statistics(self, metric, interval):
        return self._edge.clients.stats.get(metric, params={
            'interval': interval
        })
