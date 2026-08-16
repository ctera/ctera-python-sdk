import logging

from ...common import union
from .base_command import BaseCommand
from ...core.query import QueryParamBuilder
from . import query


logger = logging.getLogger('cterasdk.core')


class Buckets(BaseCommand):
    """
    Portal Storage Node APIs
    """
    default = ['name']

    def list_buckets(self, include=None):
        """
        List Buckets.

        :param list[str],optional include: List of fields to retrieve, defaults to ``['name']``
        """
        include = union(include or [], Buckets.default)
        param = QueryParamBuilder().include(include).build()
        return query.iterator(self._core, '/locations', param)