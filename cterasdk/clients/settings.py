from aiohttp import TCPConnector, CookieJar, ClientTimeout
from pydantic import ValidationError
from cterasdk import settings
from ..conf import ClientSettings, Postman
from .tracers import requests, session, postman


def get_configuration(transport_settings):
    """
    Get session configuration.
    
    :param pydantic.BaseModel transport: Transport settings
    :raises pydantic.ValidationError:
    :returns: Settings, represented as a key-value dictionary
    :rtype: dict
    """
    try:
        parameters = transport_settings.model_dump()
        ClientSettings.model_validate(parameters)

        audit = settings.audit.model_dump()
        Postman.model_validate(audit)

        parameters['audit'] = audit
        return parameters
    except AttributeError as error:
        raise
    except ValidationError as error:
        raise ValueError('Configuration error.') from error


def from_configuration(configuration):
    """
    Convert dictionary configuration to session settings.
    
    :param dict configuration: Session configuration.
    :returns: A dictionary used for initialization of an ``aiohttp.ClientSession`` object
    :rtype: dict
    """
    parameters = {}
    parameters['cookie_jar'] = CookieJar(**configuration['cookie_jar'])
    parameters['connector'] = TCPConnector(**configuration['connector'])
    parameters['timeout'] = ClientTimeout(**configuration['timeout'])
    parameters['trace_configs'] = [requests.tracer(), session.tracer()]
    if configuration['audit']['enabled']:
        parameters['trace_configs'].append(postman.tracer())
    return parameters
