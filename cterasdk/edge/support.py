from ..exception import InputError

from ..lib import FileSystem

from .. import config

from datetime import datetime

from .cli import run_cli_command

import logging

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
    
def set_debug_level(ctera_host, *levels):
        
    options = [v for k,v in DebugLevel.__dict__.items() if not k.startswith('_')]
    
    cli_command = 'dbg level'
    
    for level in levels:
        
        if not level in options:
            
            raise InputError('Invalid debug level', level, options)
            
        cli_command = cli_command + ' ' + level
    
    return run_cli_command(ctera_host, cli_command)

def get_support_report(ctera_host):

    dirpath = config.filesystem['dl']
    
    filename = 'Support-' + ctera_host.host() + datetime.now().strftime('_%Y-%m-%dT%H_%M_%S') + '.zip'
    
    logging.getLogger().info('Downloading support report. {0}'.format({'host' : ctera_host.host()}))
    
    handle = ctera_host.openfile(ctera_host._api(), '/supportreport', params = {})
    
    filepath = FileSystem.instance().save(dirpath, filename, handle)
    
    logging.getLogger().info('Support report downloaded. {0}'.format({'filepath' : filepath}))