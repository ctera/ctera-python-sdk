import logging

from .base_command import BaseCommand
from .enum import QuotaValue
from . import query
from .types import PortalAccount, QuotaRule
from ..common import union, parse_base_object_ref
from ..lib import SubfoldersQuotaResponse


logger = logging.getLogger('cterasdk.core')


class Quotas(BaseCommand):
    """
    CTERA Portal Quota Management APIs

    :ivar cterasdk.core.quotas.CloudDrives drives: Management of Cloud Drive Folder Quotas
    :ivar cterasdk.core.quotas.Subfolders subfolders: Management of subfolder Quotas
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.drives = CloudDrives(self._core)
        self.subfolders = Subfolders(self._core)


class CloudDrives(BaseCommand):

    default = ['uid', 'name', 'owner', 'folderQuota', 'isDeleted', 'folderStats']

    def all(self, include=None):
        """
        List Cloud Drive Folder Quota Rules.

        :param list[str] include: Optional list of Cloud Drive Folder attributes to include.
        :returns: A list of quota rules.
        :rtype: list[cterasdk.core.types.QuotaRule]
        """
        include = union(include or [], CloudDrives.default)
        param = query.QueryParamBuilder().include(include).orFilter(False).addFilter(
            query.FilterBuilder('folderQuota').gt(-1)
        ).build()
        for drive in query.iterator(self._core, '/cloudDrives', param):
            yield QuotaRule(
                drive.uid,
                drive.name,
                PortalAccount.from_base_object_ref(drive.owner),
                drive.folderQuota << 10,
                drive.folderStats.cloudFolderSize >> 20,
                True,
                drive.isDeleted
            )

    def add(self, name, owner, quota):
        """
        Add Cloud Drive Folder Quota Rule
        
        :param str name: Cloud Drive Folder name
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the folder
        :param int quota: Quota in GB
        """
        response = self._core.cloudfs.drives.modify(name, owner, quota=quota)
        logger.info("Quota rule added for Cloud Drive Folder '%s' and owner '%s'", name, str(owner))
        return response

    def remove(self, name, owner):
        """
        Remove Cloud Drive Folder Quota
        
        :param str name: Cloud Drive Folder name
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the folder
        """
        self._core.cloudfs.drives.modify(name, owner, quota=QuotaValue.Unlimited)
        logger.info("Quota rule removed for Cloud Drive Folder '%s' and owner '%s'", name, str(owner))


class Subfolders(BaseCommand):

    def all(self):
        """
        List Subfolder Quota Rules.

        :returns: A list of quota rules.
        :rtype: list[cterasdk.core.types.QuotaRule]
        """
        for rule in query.iterator(self._core, f'portals/{self._core.session().account.tenant}/subfolder-quotas',
                                   callback_response=SubfoldersQuotaResponse, version='v2'):
            yield QuotaRule(
                rule.cloud_drive_id,
                f'{rule.cloud_drive.name}{rule.subfolder_path}',
                PortalAccount.from_base_object_ref(rule.cloud_drive.owner.ref),
                rule.quota_mb,
                None,
                rule.should_enforce,
                False
            )

    def add(self, path, owner, quota, enforce):
        """
        Add Subfolder Quota Rule
        
        :param str path: Path
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the folder
        :param int quota: Quota in MB
        """
        parts = path.lstrip('/').split('/')
        drive = self._core.cloudfs.drives.find(parts[0], owner, include=['uid', 'owner'])
        param = {
            'cloudDriveId': drive.uid,
            'subfolderPath': f"/{'/'.join(parts[1:])}",
            'ownerId': parse_base_object_ref(drive.owner).uid,
            'quotaMb': quota,
            'shouldEnforce': enforce
        }
        response = self._core.clients.v2.post('portals/cterademo-saimon/subfolder-quotas', param)
        logger.info("Quota rule added for path '%s' and owner '%s'", path, str(PortalAccount.from_base_object_ref(drive.owner)))
        return response

    def remove(self, path, owner):
        """
        Remove Subfolder Folder Quota
        
        :param str path: Path
        :param cterasdk.core.types.UserAccount owner: User account, the owner of the folder
        """
        path = f"{path.rstrip('/')}/"
        for rule in self.all():
            if path == rule.path and rule.owner == owner:
                self._core.clients.v2.delete(f'portals/{self._core.session().account.tenant}/subfolder-quotas/{rule.volume}', params={
                    'path': "/" + path.partition("/")[2]
                })
                logger.info("Quota rule removed for path '%s' and owner '%s'", rule.path, str(rule.owner))
                return
        logger.info("Quota rule not found for path '%s' and owner '%s'", path, str(owner))