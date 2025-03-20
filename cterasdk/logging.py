import os
import sys
import logging
import cterasdk.settings

# Create package logger with NullHandler (Python best practice)
logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())

def setup_logging(stream=sys.stdout, filename=None):
    """
    Configure logging for the CTERA SDK.
    
    Args:
        stream: Output stream (default: sys.stdout)
        filename: Log to file instead of stream (optional)
    """
    parameters = {
        'format': cterasdk.settings.logging.format,
        'datefmt': cterasdk.settings.logging.date_format,
    }
    
    # Handle environment variable for backward compatibility
    env_filename = os.environ.get('cterasdk.log')
    if filename or env_filename:
        parameters['filename'] = filename or env_filename
    else:
        parameters['stream'] = stream
    
    logging.basicConfig(**parameters)
    
    # Configure individual loggers
    for logger_conf in cterasdk.settings.logging.loggers:
        logger = logging.getLogger(f'{__package__}.{logger_conf.name}')
        logger.setLevel(logging.getLevelName(logger_conf.level.upper()))

# Setup logging by default for backward compatibility
# unless explicitly disabled via environment variable
if not os.environ.get('CTERASDK_DISABLE_LOGGING'):
    setup_logging()
