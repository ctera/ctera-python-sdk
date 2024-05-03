import re
import logging

from ..common import parse_base_object_ref
from ..exceptions import CTERAException


def remote_access(device, Portal):
    device_tenant = parse_base_object_ref(device.portal).name
    device_name = device.name
    logging.getLogger('cterasdk.edge').info("Enabling remote access. %s", {'tenant': device_tenant, 'device': device_name})
    token = authn_token(Portal, device_tenant, device_name)
    device_object = create_device_object(device)
    device_object.sso(token)
    logging.getLogger('cterasdk.edge').info("Enabled remote access. %s", {'tenant': device_tenant, 'device': device_name})
    return device_object


def create_device_object(device):
    device_object = device.__class__(base=re.sub(r'^http(?=:)', 'https', device.remoteAccessUrl))
    return device_object


def authn_token(Portal, device_tenant, device_name):
    logging.getLogger('cterasdk.edge').debug("Retrieving SSO Ticket. %s", {'tenant': device_tenant, 'device': device_name})
    token = Portal.api.execute(f"/portals/{device_tenant}/devices/{device_name}", 'singleSignOn')
    if not token:
        logging.getLogger('cterasdk.edge').error('Failed to Retrieve SSO Ticket. %s', {'tenant': device_tenant, 'device': device_name})
        raise CTERAException('Failed to Retrieve SSO Ticket.')
    logging.getLogger('cterasdk.edge').debug("Retrieved SSO Ticket. %s", {'tenant': device_tenant, 'device': device_name})
    return token
