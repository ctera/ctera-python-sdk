from datetime import datetime
import logging
import cterasdk.settings

from ..lib import FileSystem
from ..exceptions import InputError
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
    """ Edge Filer Support APIs """

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
        return self._edge.cli.run_command(cli_command)

    def get_support_report(self):
        """ Download support report """
        filename = 'Support-' + self._edge.host() + datetime.now().strftime('_%Y-%m-%dT%H_%M_%S') + '.zip'
        logging.getLogger('cterasdk.edge').info('Downloading support report. %s', {'host': self._edge.host()})
        handle = self._edge.api.handle('/supportreport')
        filepath = FileSystem.instance().save(cterasdk.settings.downloads.location, filename, handle)
        logging.getLogger('cterasdk.edge').info('Support report downloaded. %s', {'filepath': filepath})
