async def listdir(edge, path, depth):
    return await edge.io.propfind(path, depth)


async def mkdir(edge, param):
    return await edge.io.mkdir(param)


async def copy(edge, source, destination, overwrite):
    return await edge.io.copy(source, destination, overwrite=overwrite)


async def move(edge, source, destination, overwrite):
    return await edge.io.move(source, destination, overwrite=overwrite)


async def delete(edge, path):
    return await edge.io.delete(path)


async def handle(edge, path):
    return await edge.io.download(path)


async def handle_many(edge, param):
    return await edge.io.download_zip('/admingui/api/status/fileManager/zip', param)


async def upload(edge, param):
    return await edge.io.upload('/actions/upload', param)
