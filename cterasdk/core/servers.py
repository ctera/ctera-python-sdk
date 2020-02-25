from .base_command import BaseCommand
from . import query
from . import union


class Servers(BaseCommand):

    default = ['name']

    def servers(self, include=None):
        # browse administration
        include = union.union(include or [], Servers.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._portal, '/servers', param)
