from unittest import mock

from cterasdk.edge import power
from tests.ut.edge import base_edge


class TestEdgePower(base_edge.BaseEdgeTest):

    def test_reboot_wait_false(self):
        self._init_filer()
        power.Power(self._filer).reboot(wait=False)
        self._filer.api.execute.assert_called_once_with("/status/device", "reboot", None)

    def test_reboot_wait_true(self):
        self._init_filer()
        self.patch_call("cterasdk.edge.power.Boot._increment")
        self._filer.test = mock.MagicMock()
        power.Power(self._filer).reboot(wait=True)
        self._filer.api.execute.assert_called_once_with("/status/device", "reboot", None)

    def test_reset_wait_false(self):
        self._init_filer()
        power.Power(self._filer).reset(wait=False)
        self._filer.api.execute.assert_called_once_with("/status/device", "reset2default", None)

    def test_reset_wait_true(self):
        self._init_filer()
        self.patch_call("cterasdk.edge.power.Boot._increment")
        self._filer.test = mock.MagicMock()
        power.Power(self._filer).reset(wait=True)
        self._filer.api.execute.assert_called_once_with("/status/device", "reset2default", None)

    def test_shutdown(self):
        self._init_filer()
        power.Power(self._filer).shutdown()
        self._filer.api.execute.assert_called_once_with("/status/device", "poweroff", None)
