import unittest
from unittest import mock

from cterasdk.core.remote import _relay_base


class TestRelayBase(unittest.TestCase):

    def _make_portal(self, baseurl):
        portal = mock.MagicMock()
        portal.ctera.baseurl = baseurl
        return portal

    def _make_device(self, name, device_dns_name=None):
        device = mock.MagicMock(spec=['name', 'deviceDnsName'] if device_dns_name is not None else ['name'])
        device.name = name
        if device_dns_name is not None:
            device.deviceDnsName = device_dns_name
        return device

    def test_fallback_when_device_dns_is_none(self):
        portal = self._make_portal('https://portal.ctera.me')
        device = self._make_device('vGateway-7192')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'https://portal.ctera.me/devices/vGateway-7192')

    def test_fallback_when_device_dns_does_not_start_with_name(self):
        portal = self._make_portal('https://portal.ctera.me')
        device = self._make_device('vGateway-7192', 'other-device.portal.ctera.me')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'https://portal.ctera.me/devices/vGateway-7192')

    def test_hostname_derivation_from_dns_name(self):
        portal = self._make_portal('https://10.0.0.1')
        device = self._make_device('vGateway-7192', 'vGateway-7192.portal.ctera.me')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'https://portal.ctera.me/devices/vGateway-7192')

    def test_non_standard_port_preserved(self):
        portal = self._make_portal('https://10.0.0.1:8443')
        device = self._make_device('vGateway-7192', 'vGateway-7192.portal.ctera.me')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'https://portal.ctera.me:8443/devices/vGateway-7192')

    def test_standard_https_port_omitted(self):
        portal = self._make_portal('https://10.0.0.1:443')
        device = self._make_device('vGateway-7192', 'vGateway-7192.portal.ctera.me')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'https://portal.ctera.me/devices/vGateway-7192')

    def test_standard_http_port_omitted(self):
        portal = self._make_portal('http://10.0.0.1:80')
        device = self._make_device('vGateway-7192', 'vGateway-7192.portal.ctera.me')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'http://portal.ctera.me/devices/vGateway-7192')

    def test_trailing_slash_in_baseurl_no_double_slash(self):
        portal = self._make_portal('https://portal.ctera.me/')
        device = self._make_device('vGateway-7192', 'vGateway-7192.portal.ctera.me')
        result = _relay_base(portal, device)
        self.assertNotIn('//', result.split('://')[1])
        self.assertEqual(result, 'https://portal.ctera.me/devices/vGateway-7192')

    def test_baseurl_with_path(self):
        portal = self._make_portal('https://10.0.0.1/api/v1')
        device = self._make_device('vGateway-7192', 'vGateway-7192.portal.ctera.me')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'https://portal.ctera.me/api/v1/devices/vGateway-7192')

    def test_substring_device_name_does_not_false_match(self):
        """A device named 'gw' should NOT match dns 'other-gw.portal.ctera.me'."""
        portal = self._make_portal('https://portal.ctera.me')
        device = self._make_device('gw', 'other-gw.portal.ctera.me')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'https://portal.ctera.me/devices/gw')

    def test_fallback_strips_trailing_slash(self):
        portal = self._make_portal('https://portal.ctera.me/')
        device = self._make_device('vGateway-7192')
        result = _relay_base(portal, device)
        self.assertEqual(result, 'https://portal.ctera.me/devices/vGateway-7192')
