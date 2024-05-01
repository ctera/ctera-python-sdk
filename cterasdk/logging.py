import os
import sys
import logging
import cterasdk.settings

parameters = {
    'format': cterasdk.settings.logging.format,
    'datefmt': cterasdk.settings.logging.date_format,
}

filename = os.environ.get('cterasdk.log')
if filename:
    parameters['filename'] = filename
else:
    parameters['stream'] = sys.stdout

logging.basicConfig(**parameters)

for logger_conf in cterasdk.settings.logging.loggers:
    logger = logging.getLogger(logger_conf.name)
    logger.setLevel(logging.getLevelName(logger_conf.level.upper()))
