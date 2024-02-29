from pathlib import Path
import yaml
from .convert import tojsonstr, fromjsonstr


sessions, downloads = None, None


def default_settings():
    global sessions, downloads  # # pylint: disable=global-statement
    with open(Path(__file__).parent.absolute().joinpath('settings.yml'), 'r', encoding='utf-8') as f:
        sdk_settings = yaml.safe_load(f)
        sessions = convert_to_object(sdk_settings['sessions'])
        downloads = convert_to_object(sdk_settings['downloads'])


def convert_to_object(data):
    return fromjsonstr(tojsonstr(data))


default_settings()
