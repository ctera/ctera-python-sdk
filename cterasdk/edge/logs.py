# pylint: disable=line-too-long
import logging

from ..lib import QueryLogsResponse
from . import query
from . import enum
from .base_command import BaseCommand


class Logs(BaseCommand):
    """
    Edge Filer Logs APIs

    :ivar list[str] default_include: Default log fields - 'severity', 'time', 'msg', 'more'
    """

    default_include = ['severity', 'time', 'msg', 'more']

    def settings(self, retention, min_severity=None):
        """
        Configure log settings

        :param int retention: Log retention period in days
        :param cterasdk.edge.enum.Severity,optional min_severity: Minimal log severity
        """
        log_config = self._edge.api.get('/config/logging/general')
        log_config.LogKeepPeriod = retention
        if min_severity:
            log_config.minSeverity = min_severity
        logging.getLogger('cterasdk.edge').info('Updating log settings. %s',
                                                {'retention': retention, 'min_severity': log_config.minSeverity})
        self._edge.api.put('/config/logging/general', log_config)
        logging.getLogger('cterasdk.edge').info('Log settings updated. %s',
                                                {'retention': retention, 'min_severity': log_config.minSeverity})

    def logs(self, topic, include=None, minSeverity=enum.Severity.INFO):
        """
        Fetch Edge Filer logs

        :param str topic: Log Topic to fetch
        :param list[str],optional include: List of fields to include in the response, defailts to Logs.default_include
        :param cterasdk.edge.enum.Severity,optional minSeverity: Minimal log severity to fetch, defaults to cterasdk.edge.enum.Severity.INFO

        :return: Log entries
        :rtype: cterasdk.lib.iterator.QueryIterator
        """
        param = query.QueryParamBuilder().include(
            include or Logs.default_include).put('topic', topic).put('minSeverity', minSeverity).build()
        return query.iterator(self._edge, '/config/logging/general', param, 'pagedQuery', QueryLogsResponse)
