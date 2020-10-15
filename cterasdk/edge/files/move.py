import logging


def move(CTERAHost, src, dest, overwrite):
    source = src.fullpath()
    destination = dest.joinpath(src.name()).fullpath()
    logging.getLogger().info('Moving. %s', {'from': source, 'to': dest.fullpath()})
    CTERAHost.move(CTERAHost.make_local_files_dir(source), CTERAHost.make_local_files_dir(destination), overwrite, use_file_url=True)
    logging.getLogger().info('Moved. %s', {'from': source, 'to': dest.fullpath(), 'fullpath': destination})
