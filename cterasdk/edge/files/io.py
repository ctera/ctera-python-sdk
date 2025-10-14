def listdir(edge, path, depth):
    return edge.io.propfind(path, depth)


def mkdir(edge, param):
    return edge.io.mkdir(param)


def copy(edge, source, destination, overwrite):
    return edge.io.copy(source, destination, overwrite=overwrite)


def move(edge, source, destination, overwrite):
    return edge.io.move(source, destination, overwrite=overwrite)


def delete(edge, path):
    return edge.io.delete(path)


def handle(edge, path):
    return edge.io.download(path)


def handle_many(edge, param):
    return edge.io.download_zip('/admingui/api/status/fileManager/zip', param)


def upload(edge, param):
    return edge.io.upload('/actions/upload', param)
