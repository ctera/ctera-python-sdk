import logging
from .base_command import BaseCommand
from . import query
from .enum import ShareGroup, PrincipalType
from .types import Share, BlockRule
from .enum import Context
from ..edge.enum import Acl
from ..common import Object
from ..cio.core.commands import GetShareCandidate


logger = logging.getLogger('cterasdk.core')


class Shares(BaseCommand):
    """
    Share Management APIs
    """

    def all(self, devices=None, protocol=None, search=None):
        """
        List Shares.

        :param list[str], optional devices: Filter results to shares belonging to one or more Edge Filers.
        :param cterasdk.core.enum.ShareProtocol, optional protocol: Filter results by share protocol.
        :param str, optional search: Return only shares matching the specified search string.

        :returns: An iterator yielding share objects.
        :rtype: generator[cterasdk.core.types.Share]
        """
        params = {}
        if devices:
            params['group_by'] = ShareGroup.Edge
        if protocol:
            params['protocol'] = protocol
        if search:
            params['search'] = search
        response = query.iterator(self._core, 'shareManagement/configurations/display', params, version='v2')

        def from_server_object(server_object):
            return Share.from_server_object(server_object)

        for item in response:
            if devices and item.group in devices:
                yield item.group, [from_server_object(share) for share in item.shares]
            yield from_server_object(item)

    def _users(self, domain, acl):

        def user_ace(user, perm):
            param = Object()
            param.permissions = perm
            param.collaborator = user
            param.collaborator._type = 'user'
            param.collaborator.type = PrincipalType.DU
            return param

        users = {ace.name: ace.perm for ace in acl}

        filters = [query.FilterBuilder('name').eq(name) for name in users.keys()]

        include = ['baseObjectRef', 'domain', 'email', 'firstName', 'lastName', 'name', 'uid', 'isTrashcan']

        return [user_ace(user, users[user.name]) for user in self._core.users.list_domain_users(domain, include, filters)] if acl else []

    def _groups(self, domain, acl):

        def group_ace(group, perm):
            param = Object()
            param.permissions = perm
            param.collaborator = group
            param.collaborator._type = 'group'
            param.collaborator.type = PrincipalType.DG
            return param
    
        groups = {ace.name: ace.perm for ace in acl}

        filters = [query.FilterBuilder('name').eq(name) for name in groups.keys()]

        include = ['baseObjectRef', 'domain', 'name', 'uid']

        return [group_ace(group, groups[group.name]) for group in self._core.groups.list_domain_groups(domain, include, filters)] if acl else []

    def _prepare_access_control_entries(self, acl, validate_acl):

        mapping = {ace.account.directory: ([], []) for ace in acl}  # group principals by domain, and type

        access_control_entries = []

        if validate_acl:

            for ace in acl:

                if ace.principal_type in [PrincipalType.DU]:
                    mapping[ace.account.directory][0].append(ace)

                if ace.principal_type in [PrincipalType.DG]:
                    mapping[ace.account.directory][1].append(ace)

            for domain, principals in mapping.items():  # for each domain, search for members and update access control entries

                users, groups = self._users(domain, principals[0]), self._groups(domain, principals[1])

                access_control_entries.extend(users)

                access_control_entries.extend(groups)

            return access_control_entries

        return [ace.to_server_object() for ace in acl]

    def add(self, name, directory, devices, acl=None, description=None, access=Acl.WindowsNT, export_to_nfs=False, nfs_krb=False,
            trusted_nfs_clients=None, krb_sec=None, block_files=None, export_to_ftp=False, validate_acl=True):
        """
        Add Share.

        :param str name: Share name
        :param str directory: Path
        :param list[str] devices: Edge filers
        :param list[cterasdk.core.types.ShareAccessControlEntry],optional acl: List of access control entries
        :param str,optional description: Description
        :param cterasdk.edge.enum.Acl,optional access: Windows File Sharing authentication mode, defaults to ``winAclMode``
        :param bool export_to_nfs: Whether to enable NFS access, defaults to ``False``
        :param list[cterasdk.core.types.NFSv3AccessControlEntry] trusted_nfs_clients: Trusted NFS v3 clients, defaults to ``None``
        :param list[cterasdk.core.enum.KRBSecurity],optional krb_sec: NFS Kerberos Security Priority
        :param bool,optional export_to_ftp: Whether to enable FTP access, defaults to ``False``
        :param list[BlockRule],optional block_files: Screen file extensions.
        :param bool,optional validate_acl: Validate ACLs with the CTERA Portal. Defaults to ``True``.

        :returns: Share ID
        :rtype: str
        """
        acl = self._prepare_access_control_entries(acl, validate_acl)

        def wrapper(core, param):
            return core.api.execute('', 'fetchGwShareCandidates', param)

        if self._core.session().context == Context.admin:
            directory = f'Users/{directory}'

        with GetShareCandidate(wrapper, self._core, directory) as metadata:
            param = Object()
            param.name = name
            param.device_ids = [device.uid for device in self._core.devices.by_name(devices, include=['uid'])]
            param.path_info = metadata
            param.access_type = access
            param.screened_file_types_enabled = False
            param.screened_file_types_rules = None
            param.acl_rules = acl
            param.export_to_nfs = export_to_nfs
            param.nfs_kerberos = nfs_krb
            param.export_to_ftp = export_to_ftp

            if description:
                param.description = description

            krb_sec = [krb_sec] if isinstance(krb_sec, str) else krb_sec
            for label, value in zip(['first', 'second', 'third'], krb_sec or []):
                setattr(param, f'nfs_sec_{label}', value)

            if trusted_nfs_clients:
                param.trusted_nfs_clients = [network.to_server_object() for network in (trusted_nfs_clients or [])]

            param.screened_file_types_rules = [rule.to_server_object() for rule in block_files] if block_files else [BlockRule.default()]

            logger.info("Creating Share. %s", {'name': name})
            response = self._core.clients.v2.post('shareManagement/configurations', param)
            logger.info("Share created. %s", {'name': name})
            return response.data.share_id

    def delete(self, *shares):
        """
        Delete Shares.

        :param list[cterasdk.core.types.Share] or str shares: List of Shares objects, or unique identifers
        """
        return self._core.clients.v2.delete('/shareManagement/configurations',
                                            [share.id if isinstance(share, Share) else share for share in shares])