import json
import logging
from pathlib import Path
import yaml
from .convert import fromjsonstr


logger = logging.getLogger('cterasdk')


settings = Path(__file__).parent.absolute().joinpath('settings.yml')
try:
    with open(settings, 'r', encoding='utf-8') as f:
        settings = fromjsonstr(json.dumps(yaml.safe_load(f)))
    core, edge, drive, io, audit = settings.core, settings.edge, settings.drive, settings.io, settings.audit
except FileNotFoundError:
    logger.fatal("Configuration file 'settings.yml' not found. Please check your installation and try again.")
    raise
