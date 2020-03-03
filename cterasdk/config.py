import os
import sys
import logging


class Logging:

    __instance = None

    @staticmethod
    def get():
        if Logging.__instance is None:
            Logging()
        return Logging.__instance

    def __init__(self):
        if Logging.__instance is not None:
            raise Exception("You must invoke Logging.get()")
        disabled = logconf['disabled']
        level = logconf['level']
        fmt = logconf['fmt']
        df = logconf['df']
        filename = logconf['filename']
        Logging.__instance = self
        self._logconf(fmt, df, filename=filename)
        logger = logging.getLogger()
        logger.disabled = disabled
        logger.level = level

    @staticmethod
    def _logconf(fmt, df, filename=None):
        basic_config_params = {
            'format': fmt,
            'datefmt': df,
        }
        if filename:
            basic_config_params['filename'] = filename
        else:
            basic_config_params['stream'] = sys.stdout

        logging.basicConfig(**basic_config_params)

    @staticmethod
    def disable():
        logging.getLogger().disabled = True

    @staticmethod
    def enable():
        logging.getLogger().disabled = False

    @staticmethod
    def setLevel(level):
        logging.getLogger().setLevel(level)

    @staticmethod
    def fmt():
        return logconf['fmt']

    @staticmethod
    def df():
        return logconf['df']


logconf = dict(
    disabled=False,
    level=logging.INFO,
    fmt='%(asctime)s,%(msecs)3d %(levelname)7s [%(filename)s:%(lineno)d] [%(funcName)s] - %(message)s',
    df='%Y-%m-%d %H:%M:%S',
    filename=os.environ.get('CTERASDK_LOG_FILE')
)

http = dict(
    timeout=20,  # http client timeout (seconds)
    retries=3,  # handle connection timeout
    ssl='Consent',  # ['Consent', 'Trust']
    verbose=False  # include request info on error
)

connect = dict(
    ssl='Consent'  # ['Consent', 'Trust']
)

filesystem = dict(
    dl='~/Downloads'
)

transcript = dict(
    disabled=True
)
