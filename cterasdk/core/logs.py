import logging
from datetime import datetime

from .base_command import BaseCommand
from ..lib import QueryLogsResponse
from ..core import enum
from ..common import Object
from . import query


class Logs(BaseCommand):
    """
    Portal Logs APIs

    :ivar cterasdk.core.logs.Alerts alerts: Object holding the Portal Log Based Alerts APIs
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.alerts = Alerts(self._core)

    def device(self,
               name,
               topic=enum.LogTopic.System,
               min_severity=enum.Severity.INFO,
               before=None,
               after=None,
               filters=None):
        """
        Get device logs from the Portal

        :param str name: Name of a device
        :param cterasdk.core.enum.LogTopic,optional topic: Log topic to get, defaults to cterasdk.core.enum.LogTopic.System
        :param cterasdk.core.enum.Severity,optional min_severity:
         Minimun severity of logs to get, defaults to cterasdk.core.enum.Severity.INFO
        :param str,optional before: Get logs before this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param str,optional after: Get logs after this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param list[cterasdk.core.query.FilterBuilder],optional filters: List of additional filters, defaults to None

        :return: Iterator for all matching logs
        :rtype: cterasdk.lib.iterator.Iterator[cterasdk.object.Object]
        """
        return self.get(topic, min_severity, enum.OriginType.Device, name, before, after, filters)

    def get(self, topic=enum.LogTopic.System, min_severity=enum.Severity.INFO, origin_type=enum.OriginType.Portal, origin=None,
            before=None, after=None, filters=None):
        """
        Get logs from the Portal

        :param cterasdk.core.enum.LogTopic,optional topic: Log topic to get, defaults to cterasdk.core.enum.LogTopic.System
        :param cterasdk.core.enum.Severity,optional min_severity:
         Minimun severity of logs to get, defaults to cterasdk.core.enum.Severity.INFO
        :param cterasdk.core.enum.OriginType,optional origin_type:
         Origin type of the logs to get, defaults to cterasdk.core.enum.OriginType.Portal
        :param str,optional origin: Log origin (e.g. device name, Portal server name), defaults to None
        :param str,optional before: Get logs before this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param str,optional after: Get logs after this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param list[cterasdk.core.query.FilterBuilder],optional filters: List of additional filters, defaults to None

        :return: Iterator for all matching logs
        :rtype: cterasdk.lib.iterator.Iterator[cterasdk.object.Object]
        """
        builder = query.QueryParamBuilder().put('topic', topic).put('minSeverity', min_severity)

        builder.addFilter(query.FilterBuilder('originType').eq(origin_type))

        if before is not None:
            builder.addFilter(query.FilterBuilder('time').before(self._strptime(before)))

        if after is not None:
            builder.addFilter(query.FilterBuilder('time').after(self._strptime(after)))

        if origin is not None:
            builder.addFilter(query.FilterBuilder.ref('origin').eq(origin))

        if filters:
            for user_filter in filters:
                builder.addFilter(user_filter)

        return query.iterator(self._core, '', builder.build(), 'queryLogs', callback_response=QueryLogsResponse)

    @staticmethod
    def _strptime(datetime_str):
        try:
            return datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
        except ValueError as error:
            raise error


class Alerts(BaseCommand):
    """
    Portal Log Based Alerts APIs
    """

    def add(self, name, description=None, topic=None, log=None, min_severity=None, origin_type=None, content=None):
        """
        Add a Log Based Alert

        :param str name: Alert name
        :param str,optional description: Alert description
        :param cterasdk.core.enum.LogTopic,optional topic: Log topic to get, defaults to any topic
        :param str,optional log: Class name of the log
        :param cterasdk.core.enum.Severity,optional min_severity: Minimun severity for triggering an alert, defaults to any severity
        :param cterasdk.core.enum.OriginType,optional origin_type: Origin type of the log, defaults to any origin
        :param str content: Content of the log message
        :returns: A list of alerts
        :rtype: list[cterasdk.common.object.Object]
        """
        alert = Object()
        alert.id = name
        alert._classname = 'AlertRule'  # pylint: disable=protected-access
        if description:
            alert.description = description
        if log:
            alert.logName = log
        if content:
            alert.messageContent = content
        if min_severity:
            alert.minSeverity = min_severity
        if origin_type:
            alert.originType = origin_type
        if topic:
            alert.topic = topic
        alerts = self.get()
        alerts.append(alert)
        return self.put(alerts)

    def put(self, alerts):
        """
        Set Log Based Alerts
         Use :func:`cterasdk.core.types.AlertBuilder` to build log based alerts

        :param list[cterasdk.core.types.Alert] alerts: List of alerts
        """
        logging.getLogger('cterasdk.core').info('Updating log based alerts.')
        response = self._core.api.put(self._context, alerts)
        logging.getLogger('cterasdk.core').info('Log based alerts updated.')
        return response

    def get(self):
        """
        Get a List of Log Based Alerts

        :returns: A list of alerts
        :rtype: list[cterasdk.common.object.Object]
        """
        return self._core.api.get(self._context)

    def delete(self, name):
        """
        Remove a Log Based Alert

        :param str name: Alert name
        """
        alerts = [alert for alert in self.get() if alert.id != name]
        self.put(alerts)

    @property
    def _context(self):
        return f'{"" if self._core.session().in_tenant_context() else "/settings"}/alerts'
