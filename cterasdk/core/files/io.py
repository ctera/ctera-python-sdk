from ...cio import core as fs


def listdir(core, param):
    return core.api.execute('', 'fetchResources', param)


def versions(core, path):
    return core.api.execute('', 'listSnapshots', path)


def mkdir(core, param):
    return core.api.execute('', 'makeCollection', param)


def delete(core, param):
    return core.api.execute('', 'deleteResources', param)


def undelete(core, param):
    return core.api.execute('', 'restoreResources', param)


def copy(core, param):
    return core.api.execute('', 'copyResources', param)


def move(core, param):
    return core.api.execute('', 'moveResources', param)


def handle(core, param):
    return core.io.download(param)


def handle_many(core, param, directory):
    with fs.EnsureDirectory(listdir, core, directory) as (_, resource):
        return core.io.download_zip(str(resource.cloudFolderInfo.uid), param)


def upload(core, cloudfolder, param):
    return core.io.upload(cloudfolder, param)


def _search_collaboration_member(core, param):
    return core.api.execute('', 'searchCollaborationMembers', param)


def remove_share_recipients(core, path, members):
    with fs.GetShareMetadata(list_shares, core, path) as shares:
        return fs.RemoveMembers(update_share, core, path, shares, members).execute()


def list_shares(core, param):
    return core.api.execute('', 'listShares', param)


def update_share(core, param):
    return core.api.execute('', 'shareResource', param)


def share(core, path, members, as_project, allow_reshare, allow_sync):
    with fs.GetMetadata(listdir, core, path) as (_, resource):
        with fs.FilterShareMembers(_search_collaboration_member, core, members, resource.cloudFolderInfo.uid) as collaborators:
            return fs.Share(update_share, core, path, collaborators, as_project, allow_reshare, allow_sync).execute()


def add_share_recipients(core, path, members):
    with fs.GetMetadata(listdir, core, path) as (_, resource):
        with fs.GetShareMetadata(list_shares, core, path) as shares:
            with fs.FilterShareMembers(_search_collaboration_member, core, members, resource.cloudFolderInfo.uid) as collaborators:
                return fs.AddMembers(update_share, core, path, shares, collaborators).execute()


def public_link(core, param):
    return core.api.execute('', 'createShare', param)
