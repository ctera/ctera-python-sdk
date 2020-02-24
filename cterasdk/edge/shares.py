import logging

from .enum import PrincipalType, FileAccessMode
from .files import path
from ..common import Object
from ..exception import CTERAException, InputError


def add(ctera_host,
        name,
        directory,
        acl,
        access,
        csc,
        dirPermissions,
        comment,
        exportToAFP,
        exportToFTP,
        exportToNFS,
        exportToPCAgent,
        exportToRSync,
        indexed
        ):  # pylint: disable=too-many-arguments,too-many-locals

    param = Object()
    param.name = name

    parts = path.CTERAPath(directory, '/').parts()
    volume = parts[0]
    validate_root_directory(ctera_host, volume)
    param.volume = volume

    directory = '/'.join(parts[1:])
    param.directory = directory

    param.access = access
    param.dirPermissions = dirPermissions
    param.exportToAFP = exportToAFP
    param.exportToFTP = exportToFTP
    param.exportToNFS = exportToNFS
    param.exportToPCAgent = exportToPCAgent
    param.exportToRSync = exportToRSync
    param.indexed = indexed
    param.comment = comment

    param.acl = []
    for entry in acl:
        if len(entry) != 3:
            raise InputError('Invalid input', repr(entry), '[("type", "name", "perm"), ...]')
        addShareACLRule(param.acl, entry[0], entry[1], entry[2])

    try:
        ctera_host.add('/config/fileservices/share', param)
        logging.getLogger().info("Share created. %s", {'name': name})
    except Exception as error:
        logging.getLogger().error("Share creation failed.")
        raise CTERAException('Share creation failed', error)


def validate_root_directory(ctera_host, name):
    param = Object()
    param.path = '/'

    response = ctera_host.execute('/status/fileManager', 'listPhysicalFolders', param)
    for root in response:
        if root.fullpath == ('/%s' % name):
            logging.getLogger().debug("Found root directory. %s", {'name': root.name, 'type': root.type, 'fullpath': root.fullpath})
            return name

    logging.getLogger().error("Could not find root directory. %s", {'name': name})

    options = [root.fullpath[1:] for root in response]
    raise InputError('Invalid root directory.', name, options)


def addShareACLRule(acls, principal_type_field, name, perm):
    ace = Object()
    ace._classname = "ShareACLRule"  # pylint: disable=protected-access
    ace.principal2 = Object()

    options = {k: v for k, v in PrincipalType.__dict__.items() if not k.startswith('_')}
    principal_type = options.get(principal_type_field)
    if principal_type == PrincipalType.LU:
        ace.principal2._classname = PrincipalType.LU  # pylint: disable=protected-access
        ace.principal2.ref = "#config#auth#users#" + name
    elif principal_type == PrincipalType.LG:
        ace.principal2._classname = PrincipalType.LG  # pylint: disable=protected-access
        ace.principal2.ref = "#config#auth#groups#" + name
    elif principal_type == PrincipalType.DU:
        ace.principal2._classname = PrincipalType.DU  # pylint: disable=protected-access
        ace.principal2.name = name
    elif principal_type == PrincipalType.DG:
        ace.principal2._classname = PrincipalType.DG  # pylint: disable=protected-access
        ace.principal2.name = name
    else:
        raise InputError('Invalid principal type', principal_type_field, list(options.keys()))

    ace.permissions = Object()
    ace.permissions._classname = "FileAccessPermissions"  # pylint: disable=protected-access

    options = {k: v for k, v in FileAccessMode.__dict__.items() if not k.startswith('_')}
    permission = options.get(perm)
    if permission is not None:
        ace.permissions.allowedFileAccess = permission
    else:
        raise InputError('Invalid permission', perm, list(options.keys()))

    acls.append(ace)

    return acls


def add_acl(ctera_host, name, acl):
    current_acl = ctera_host.get('/config/fileservices/share/' + name + '/acl')

    new_acl_dict = {}
    for entry in acl:
        temp_acl = []
        if len(entry) != 3:
            raise InputError('Invalid input', repr(entry), '[("type", "name", "perm"), ...]')
        addShareACLRule(temp_acl, entry[0], entry[1], entry[2])
        entry_key = entry[0] + '#' + entry[1]
        new_acl_dict[entry_key] = temp_acl[0]

    for entry in current_acl:
        ace_type = entry.principal2._classname  # pylint: disable=protected-access
        if ace_type in [PrincipalType.LU, PrincipalType.LG]:
            ace_name = entry.principal2.ref
            ace_name = ace_name[ace_name.rfind('#') + 1:]
        else:
            ace_name = entry.principal2.name
        entry_key = ace_type + '#' + ace_name

        if entry_key not in new_acl_dict:
            new_acl_dict[entry_key] = entry

    acl = [v for k, v in new_acl_dict.items()]
    ctera_host.put('/config/fileservices/share/' + name + '/acl', acl)


def remove_acl(ctera_host, name, tuples):
    current_acl = ctera_host.get('/config/fileservices/share/' + name + '/acl')

    options = {v: k for k, v in PrincipalType.__dict__.items() if not k.startswith('_')}  # reverse
    new_acl = []
    for entry in current_acl:
        ace_type = entry.principal2._classname  # pylint: disable=protected-access
        if ace_type in [PrincipalType.LU, PrincipalType.LG]:
            ace_name = entry.principal2.ref
            ace_name = ace_name[ace_name.rfind('#') + 1:]
        else:
            ace_name = entry.principal2.name

        if (options.get(ace_type), ace_name) not in tuples:
            new_acl.append(entry)

    ctera_host.put('/config/fileservices/share/' + name + '/acl', new_acl)


def delete(ctera_host, name):
    try:
        ctera_host.delete('/config/fileservices/share/' + name)
        logging.getLogger().info("Share deleted. %s", {'name': name})
    except Exception as error:
        logging.getLogger().error("Share deletion failed.")
        raise CTERAException('Share deletion failed', error)
