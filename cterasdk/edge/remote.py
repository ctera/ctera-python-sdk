import re
import logging

from ..common import parse_base_object_ref
from ..exception import CTERAException


def remote_access(device, Portal):
    device_tenant = parse_base_object_ref(device.portal).name
    device_name = device.name
    logging.getLogger().info("Enabling remote access. %s", {'tenant': device_tenant, 'device': device_name})
    token = authn_token(Portal, device_tenant, device_name)
    device_object = create_device_object(device)
    authn_device_session(device_object, token)
    logging.getLogger().info("Enabled remote access. %s", {'tenant': device_tenant, 'device': device_name})
    device_object.session().start_local_session(device_object)
    return device_object


def create_device_object(device):
    device_object = device.__class__(uri=re.sub(r'^http(?=:)', 'https', device.remoteAccessUrl))
    return device_object


def authn_token(Portal, device_tenant, device_name):
    logging.getLogger().debug("Retrieving SSO Ticket. %s", {'tenant': device_tenant, 'device': device_name})
    token = Portal.execute(f"/portals/{device_tenant}/devices/{device_name}", 'singleSignOn')
    if not token:
        logging.getLogger().error('Failed to Retrieve SSO Ticket. %s', {'tenant': device_tenant, 'device': device_name})
        raise CTERAException('Failed to Retrieve SSO Ticket.')
    logging.getLogger().debug("Retrieved SSO Ticket. %s", {'tenant': device_tenant, 'device': device_name})
    return token


def authn_device_session(device_object, token):
    logging.getLogger().debug("Logging in using SSO Ticket.")
    device_object.get('/ssologin', {'ticket': token})