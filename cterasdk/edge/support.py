from datetime import datetime
import logging

from ..exception import InputError
from ..lib import FileSystem
from .. import config
from .base_command import BaseCommand


class DebugLevel:
    none = "none"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"
    process = "process"
    samba = "samba"
    aapi = "aapi"
    storage = "storage"
    upload = "upload"
    http = "http"
    dns = "dns"
    ntp = "ntp"
    backup = "backup"
    db = "db"
    files = "files"
    cttp = "cttp"
    cttp_data = "cttp_data"
    rsync = "rsync"
    alert = "alert"
    cbck = "cbck"
    av = "av"
    index = "index"
    auth = "auth"
    license = "license"
    collaboration = "collaboration"
    error_abort = "error_abort"
    cloud_extender = "cloud_extender"
    apps = "apps"
    evictor = "evictor"
    evictor_verbose = "evictor_verbose"
    caching = "caching"


class Support(BaseCommand):
    """ Gateway Support APIs """

    def set_debug_level(self, *levels):
        """
        Set the debug level
        """
        options = [v for k, v in DebugLevel.__dict__.items() if not k.startswith('_')]
        cli_command = 'dbg level'
        for level in levels:
            if level not in options:
                raise InputError('Invalid debug level', level, options)
            cli_command = cli_command + ' ' + level
        return self._gateway.cli.run_command(cli_command)

    def get_support_report(self):
        """ Download support report """
        dirpath = config.filesystem['dl']
        filename = 'Support-' + self._gateway.host() + datetime.now().strftime('_%Y-%m-%dT%H_%M_%S') + '.zip'
        logging.getLogger().info('Downloading support report. %s', {'host': self._gateway.host()})
        handle = self._gateway.openfile('/supportreport')
        filepath = FileSystem.instance().save(dirpath, filename, handle)
        logging.getLogger().info('Support report downloaded. %s', {'filepath': filepath})
