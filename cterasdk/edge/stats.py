import logging

from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


VALID_STAT_TYPES = ('cpu', 'memory', 'cache', 'volume', 'connections', 'local_io', 'disk_io', 'cloud_io')
VALID_INTERVALS = ('hour', 'day', 'week', 'month', 'year', 'last')


class Stats(BaseCommand):
    """
    Edge Filer statistics retrieved via the HTTP Relay channel.

    Valid stat types: cpu, memory, cache, volume, connections, local_io, disk_io, cloud_io
    Valid intervals: hour, day, week, month, year, last
    """

    def get(self, stat_type, interval='hour'):
        """
        Get device statistics

        :param str stat_type: Statistic type.
         Options: ``cpu``, ``memory``, ``cache``, ``volume``, ``connections``, ``local_io``, ``disk_io``, ``cloud_io``
        :param str,optional interval: Time interval, defaults to ``hour``.
         Options: ``hour``, ``day``, ``week``, ``month``, ``year``, ``last``
        :returns: Statistics data
        """
        if stat_type not in VALID_STAT_TYPES:
            raise ValueError(f'Invalid stat_type {stat_type!r}. Valid: {VALID_STAT_TYPES}')
        if interval not in VALID_INTERVALS:
            raise ValueError(f'Invalid interval {interval!r}. Valid: {VALID_INTERVALS}')
        return self._edge.api.get(f'/stats/{stat_type}', params={'interval': interval})
