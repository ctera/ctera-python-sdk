import logging
from .base_command import BaseCommand
from ...common import union
from ...core.query import QueryParamBuilder
from . import query


logger = logging.getLogger('cterasdk.core')


class Plans(BaseCommand):
    """
    Portal Plan APIs

    :ivar cterasdk.core.plans.PlanAutoAssignPolicy auto_assign: Object holding the Portal subscription plan auto assignment rules APIs
    """
    default = ['name']

    def list_plans(self, include=None, filters=None):
        """
        List Plans

        :param list[str],optional include: List of fields to retrieve, defaults to ['name']
        :param list[],optional filters: List of additional filters, defaults to None

        :return: Iterator for all matching Plans
        :rtype: cterasdk.asynchronous.core.iterator.QueryAsyncIterator
        """
        include = union(include or [], Plans.default)
        builder = QueryParamBuilder().include(include)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        builder.orFilter((len(filters) > 1))
        param = builder.build()
        return query.iterator(self._core, '/plans', param)
