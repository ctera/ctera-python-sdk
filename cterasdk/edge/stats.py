import logging

from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


VALID_STAT_TYPES = ('cpu', 'memory', 'cache', 'volume', 'connections', 'local_io', 'disk_io', 'cloud_io')
VALID_INTERVALS = ('hour', 'day', 'week', 'month', 'year', 'last')


class Stats(BaseCommand):

    def get(self, stat_type, interval='hour'):
        if stat_type not in VALID_STAT_TYPES:
            raise ValueError(f'Invalid stat_type {stat_type!r}. Valid: {VALID_STAT_TYPES}')
        if interval not in VALID_INTERVALS:
            raise ValueError(f'Invalid interval {interval!r}. Valid: {VALID_INTERVALS}')
        return self._edge.api.get(f'/stats/{stat_type}', params={'interval': interval})
