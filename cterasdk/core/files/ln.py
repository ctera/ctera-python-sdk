import logging
from ...common import DateTimeUtils

from .common import CreateShareParam


def mklink(ctera_host, path, access, expire_in):
    access = {'RO': 'ReadOnly', 'RW': 'ReadWrite', 'PO': 'PreviewOnly'}.get(access)
    expire_on = DateTimeUtils.get_expiration_date(expire_in).strftime('%Y-%m-%d')

    logging.getLogger().info('Creating public link. %s', {'path': str(path.relativepath), 'access': access, 'expire_on': expire_on})

    param = CreateShareParam.instance(path=path.fullpath(), access=access, expire_on=expire_on)

    response = ctera_host.execute('', 'createShare', param)

    return response.publicLink
