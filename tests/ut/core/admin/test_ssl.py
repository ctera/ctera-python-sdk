import munch
from cterasdk.core import ssl
from tests.ut.core.admin import base_admin


class TestCoreSSL(base_admin.BaseCoreTest):

    def test_get_certificate(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = ssl.SSL(self._global_admin).get()
        self._global_admin.api.get.assert_called_once_with('/settings/ca')
        self.assertEqual(ret, get_response)

    def test_thumbprint(self):
        thumbprint = 'thumbprint'
        get_response = munch.Munch({'thumbprint': thumbprint})
        self._init_global_admin(get_response=get_response)
        ret = ssl.SSL(self._global_admin).thumbprint
        self._global_admin.api.get.assert_called_once_with('/settings/ca')
        self.assertEqual(ret, thumbprint)

    def test_export_certificate(self):
        destination = '/home/user'
        filename = 'certificate.zip'
        mock_split_file_directory = self.patch_call('cterasdk.core.ssl.FileSystem.generate_file_location')
        mock_split_file_directory.return_value = (destination, filename)
        mock_save = self.patch_call('cterasdk.core.ssl.FileSystem.save')
        mock_save.return_value = f'{destination}/{filename}'
        handle_response = 'handle'
        self._init_setup(handle_response=handle_response)
        ret = ssl.SSL(self._global_admin).export(destination=destination)
        mock_split_file_directory.assert_called_once_with(destination, filename)
        mock_save.assert_called_once_with(destination, filename, handle_response)
        self._global_admin.ctera.handle.assert_called_once_with('/preview/exportCertificate')
        self.assertEqual(ret, f'{destination}/{filename}')
