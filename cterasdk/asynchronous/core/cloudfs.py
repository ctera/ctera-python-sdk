from .base_command import BaseCommand
from . import query
from ...core.query import QueryParamBuilder, FilterBuilder
from ...common.utils import union


class CloudFS(BaseCommand):
    """
    CloudFS APIs

    :ivar cterasdk.core.cloudfs.CloudDrives drives: Object holding Cloud Drive Folders APIs
    """

    def __init__(self, core):
        super().__init__(core)
        self.drives = CloudDrives(self._core)


class CloudDrives(BaseCommand):
    """ Cloud Drive Folder APIs """

    default = ['name']

    async def find(self, name, owner, include=None):
        """
        Find a Cloud Drive Folder

        :param str name: Name of the Cloud Drive Folder to find
        :param cterasdk.core.types.UserAccount owner: User account of the folder group owner
        :param list[str] include: List of metadata fields to include in the response

        :returns: A Cloud Drive Folder
        """

        user = await self._core.users.get(owner, ['uid'])
        include = union(include or [], CloudDrives.default)
        builder = QueryParamBuilder().include(include).ownedBy(user.uid)
        builder.addFilter(FilterBuilder('name').eq(name))
        param = builder.build()
        return query.iterator(self._core, '/cloudDrives', param)
