import logging

from . import query
from .base_command import BaseCommand
from ..lib import QuotaResponse
from .types import QuotaRule


logger = logging.getLogger('cterasdk.edge')


class Quotas(BaseCommand):
    """
    Edge Filer Quota Management APIs
    """

    def all(self):
        """
        List Cloud Drive Folder Quota Rules.

        :returns: A list of quota rules.
        :rtype: list[cterasdk.edge.types.QuotaRule]
        """
        param = query.QueryParamBuilder().countLimit(150).build()
        for rule in query.iterator(self._edge, '/config/cloudsync', param, 'localquotadb_getQuotaState', QuotaResponse):
            policy = rule.quotaEntity
            yield QuotaRule(
                f'{policy.folderName}/{policy.relPath}' if policy.relPath else policy.folderName,
                policy.ownerName,
                policy.localUsage,
                -1 if not policy.relPath else policy.cloudRemaining >> 20,
                policy.enforceQuota
            )
