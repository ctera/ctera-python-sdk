from unittest import mock
import munch

from cterasdk.edge import ssh
from tests.ut import base_edge


class TestEdgeSSH(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._public_key_string = "public_key"
        self._public_key_file = "./public_key_file.ley"
        self._exponent = 65537
        self._key_size = 2048
        

    def test_enable_public_key_from_string(self):
        self._init_filer()
        ssh.SSH(self._filer).enable(self._public_key_string)
        self._filer.api.execute.assert_called_once_with('/config/device', 'startSSHD', mock.ANY)
        expected_param = munch.Munch({'publicKey': self._public_key_string})
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_no_public_key(self):
        response = 'PublicKey'
        mock_generate_and_save_key_pair = self.patch_call('cterasdk.edge.ssh.CryptoServices.generate_and_save_key_pair')
        mock_generate_and_save_key_pair.return_value = response
        self._init_filer()
        ssh.SSH(self._filer).enable()
        mock_generate_and_save_key_pair.assert_called_once_with(self._filer.host(), exponent=self._exponent, key_size=self._key_size)
        self._filer.api.execute.assert_called_once_with('/config/device', 'startSSHD', mock.ANY)
        expected_param = munch.Munch({'publicKey': response})
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_public_key_from_file(self):
        response = 'PublicKey'
        self._init_filer()
        with mock.patch("builtins.open", mock.mock_open(read_data=response)):
            ssh.SSH(self._filer).enable(public_key_file=self._public_key_file)
            self._filer.api.execute.assert_called_once_with('/config/device', 'startSSHD', mock.ANY)
            expected_param = munch.Munch({'publicKey': response})
            actual_param = self._filer.api.execute.call_args[0][2]
            self._assert_equal_objects(actual_param, expected_param)

    def test_disable(self):
        self._init_filer()
        ssh.SSH(self._filer).disable()
        self._filer.api.execute.assert_called_once_with('/config/device', 'stopSSHD')
