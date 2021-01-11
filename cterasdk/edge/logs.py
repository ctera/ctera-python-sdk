# pylint: disable=line-too-long
import logging

from ..lib import Command, Iterator
from . import query
from . import enum
from .base_command import BaseCommand


class Logs(BaseCommand):
    """
    Gateway Logs APIs

    :ivar list[str] default_include: Default log fields - 'severity', 'time', 'msg', 'more'
    """

    default_include = ['severity', 'time', 'msg', 'more']

    def settings(self, retention, min_severity=None):
        """
        Configure log settings

        :param int retention: Log retention period in days
        :param cterasdk.edge.enum.Severity,optional min_severity: Minimal log severity
        """
        log_config = self._gateway.get('/config/logging/general')
        log_config.LogKeepPeriod = retention
        if min_severity:
            log_config.minSeverity = min_severity
        logging.getLogger().info('Updating log settings. %s', {'retention': retention, 'min_severity': log_config.minSeverity})
        self._gateway.put('/config/logging/general', log_config)
        logging.getLogger().info('Log settings updated. %s', {'retention': retention, 'min_severity': log_config.minSeverity})

    def logs(self, topic, include=None, minSeverity=enum.Severity.INFO):
        """
        Fetch Gateway logs

        :param str topic: Log Topic to fetch
        :param list[str],optional include: List of fields to include in the response, defailts to Logs.default_include
        :param cterasdk.edge.enum.Severity,optional minSeverity: Minimal log severity to fetch, defaults to cterasdk.edge.enum.Severity.INFO

        :return: Log lines
        :rtype: cterasdk.lib.iterator.Iterator
        """
        param = query.QueryParamBuilder().include(
            include or Logs.default_include).put('topic', topic).put('minSeverity', minSeverity).build()
        function = Command(self._query_logs)
        return Iterator(function, param)

    def _query_logs(self, param):
        response = self._gateway.execute('/config/logging/general', 'pagedQuery', param)
        return (response.hasMore, response.logs)
