import logging

from ...common import parse_base_object_ref
from ...exceptions import CTERAException


logger = logging.getLogger('cterasdk.remote')


class RemoteClients:

    def __init__(self, device, Portal, api_client):
        self._device = device
        self._Portal = Portal
        self._authenticated = False
        self._api = api_client

    @property
    def api(self):
        if self._Portal and not self._authenticated:
            tenant = parse_base_object_ref(self._device.portal).name
            device_name = self._device.name
            logger.debug('Auto-SSO login via relay channel. %s', {'tenant': tenant, 'device': device_name})
            token = self._Portal.api.execute(f'/portals/{tenant}/devices/{device_name}', 'singleSignOn')
            if not token:
                raise CTERAException('Failed to Retrieve SSO Ticket.')
            self._api.get('/ssologin', params={'ticket': token})
            self._authenticated = True
        return self._api
