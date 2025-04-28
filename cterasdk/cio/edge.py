import logging
from ..common import Object
from . import common, exceptions


logger = logging.getLogger('cterasdk.edge')


class EdgePath(common.BasePath):
    """Path for CTERA Edge Filer"""

    @staticmethod
    def instance(scope, reference):
        return EdgePath(scope, reference)


def create_listdir_parameter(path):
    param = Object()
    param.path = path
    return param


def accept_response(response, reference):
    error = {
        "File exists": exceptions.ResourceExistsError(),
        "Creating a folder in this location is forbidden": exceptions.RestrictedPathError(),
    }.get(response, None)
    try:
        if error:
            raise error
    except exceptions.ResourceExistsError as error:
        logger.warning('Resource already exists: a file or folder with this name already exists. %s', {'path': reference})
        raise error
    except exceptions.RestrictedPathError as error:
        logger.error('Creating a folder in the specified location is forbidden. %s', {'name': reference})
        raise error