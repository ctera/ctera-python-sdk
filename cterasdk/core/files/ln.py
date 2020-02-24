from datetime import datetime, timedelta
import logging

from .common import CreateShareParam


def mklink(ctera_host, path, access, expire_in):
    access = {'RO': 'ReadOnly', 'RW': 'ReadWrite', 'PO': 'PreviewOnly'}.get(access)
    expire_on = datetime.now() + timedelta(days=expire_in)
    expire_on = expire_on.strftime('%Y-%m-%d')

    logging.getLogger().info('Creating public link. %s', {'path': path, 'access': access, 'expire_on': expire_on})

    param = CreateShareParam.instance(path=path.fullpath(), access=access, expire_on=expire_on)

    response = ctera_host.execute('', 'createShare', param)

    return response.publicLink
