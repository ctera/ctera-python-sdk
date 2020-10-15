import logging


def copy(CTERAHost, src, dest, overwrite):
    source = src.fullpath()
    destination = dest.joinpath(src.name()).fullpath()
    logging.getLogger().info('Copying. %s', {'from': source, 'to': dest.fullpath()})
    CTERAHost.copy(CTERAHost.make_local_files_dir(source), CTERAHost.make_local_files_dir(destination), overwrite, use_file_url=True)
    logging.getLogger().info('Copied. %s', {'from': source, 'to': dest.fullpath(), 'fullpath': destination})
