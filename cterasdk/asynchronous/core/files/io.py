from ....cio import core as fs


async def listdir(core, param):
    return await core.v1.api.execute('', 'fetchResources', param)


async def versions(core, path):
    return await core.v1.api.execute('', 'listSnapshots', path)


async def mkdir(core, param):
    return await core.v1.api.execute('', 'makeCollection', param)


async def delete(core, param):
    return await core.v1.api.execute('', 'deleteResources', param)


async def undelete(core, param):
    return await core.v1.api.execute('', 'restoreResources', param)


async def copy(core, param):
    return await core.v1.api.execute('', 'copyResources', param)


async def move(core, param):
    return await core.v1.api.execute('', 'moveResources', param)


async def handle(core, param):
    return await core.io.download(param)


async def handle_many(core, param, directory):
    async with fs.EnsureDirectory(listdir, core, directory) as (_, resource):
        return await core.io.download_zip(str(resource.cloudFolderInfo.uid), param)


async def upload(core, cloudfolder, param):
    return await core.io.upload(cloudfolder, param)


async def _search_collaboration_member(core, param):
    return await core.v1.api.execute('', 'searchCollaborationMembers', param)


async def remove_share_recipients(core, path, members):
    shares = await fs.GetShareMetadata(list_shares, core, path).a_execute()
    return await fs.RemoveMembers(update_share, core, path, shares, members).a_execute()


async def list_shares(core, param):
    return await core.v1.api.execute('', 'listShares', param)


async def update_share(core, param):
    return await core.v1.api.execute('', 'shareResource', param)


async def share(core, path, members, as_project, allow_reshare, allow_sync):
    async with fs.GetMetadata(listdir, core, path) as (_, resource):
        async with fs.FilterShareMembers(_search_collaboration_member, core, members, resource.cloudFolderInfo.uid) as members:
            return await fs.Share(update_share, core, path, members, as_project, allow_reshare, allow_sync).a_execute()


async def add_share_recipients(core, path, members):
    async with fs.GetMetadata(listdir, core, path) as (_, resource):
        async with fs.GetShareMetadata(list_shares, core, path) as shares:
            async with fs.FilterShareMembers(_search_collaboration_member, core, members, resource.cloudFolderInfo.uid) as members:
                return await fs.AddMembers(update_share, core, path, shares, members).a_execute()


async def public_link(core, param):
    return await core.v1.api.execute('', 'createShare', param)
