import logging

from .base_command import BaseCommand
from ..lib import FileSystem
from ..common import Object


class SSL(BaseCommand):
    """ Gateway SSL APIs """

    BEGIN_PEM = '-----BEGIN'

    def enable_http(self):
        """
        Enable HTTP access
        """
        self._set_force_https(False)

    def disable_http(self):
        """
        Disable HTTP access
        """
        self._set_force_https(True)

    def is_http_disabled(self):
        """
        Check if HTTP access is disabled
        """
        return self._get_force_https()

    def is_http_enabled(self):
        """
        Check if HTTP access is enabled
        """
        return not self._get_force_https()

    def _get_force_https(self):
        return self._gateway.get('/config/fileservices/webdav/forceHttps')

    def _set_force_https(self, force):
        self._gateway.put('/config/fileservices/webdav/forceHttps', force)

    def remove_storage_ca(self):
        """
        Remove object storage trusted CA certificate
        """
        self._gateway.put('/config/extStorageTrustedCA', None)

    def get_storage_ca(self):
        """
        Get object storage trusted CA certificate
        """
        return self._gateway.get('/status/extStorageTrustedCA')

    def set_storage_ca(self, certificate):
        """
        Set object storage trusted CA certificate

        :param str certificate: The PEM-encoded certificate or a path to the PEM-encoded server certificate file
        """
        logging.getLogger().info('Setting trusted object storage CA certificate')
        param = Object()
        param._classname = 'ExtTrustedCA'  # pylint: disable=protected-access
        param.certificate = SSL._obtain_secret(certificate)
        return self._gateway.put('/config/extStorageTrustedCA', param)

    def set_certificate(self, private_key, *certificates):
        """
        Set the Edge Filer's web server's certificate.

        :param str private_key: The PEM-encoded private key or a path to the PEM-encoded private key file
        :param list[str] certificates: The PEM-encoded certificates or a path to the PEM-encoded certificates
        """
        logging.getLogger().debug('Loading private key')
        certificate_chain = [SSL._obtain_secret(private_key)]
        logging.getLogger().debug('Loading certificates')
        certificate_chain = certificate_chain + [SSL._obtain_secret(certificate) for certificate in certificates]

        logging.getLogger().info("Uploading certificate chain")
        server_certificate = '\n' + '\n'.join(certificate_chain).replace('\n\n', '\n')
        response = self._gateway.put('/config/certificate', server_certificate)
        logging.getLogger().info("Uploaded certificate chain")
        return response

    @staticmethod
    def _obtain_secret(secret):
        if not secret.startswith(SSL.BEGIN_PEM):
            file_info, secret = SSL._file_contents(secret)
            logging.getLogger().debug(
                "Reading file. %s", {'name': file_info['name'], 'size': file_info['size'], 'type': file_info['mimetype']}
            )
        return secret

    @staticmethod
    def _file_contents(filepath):
        file_info = FileSystem.instance().get_local_file_info(filepath)
        file_content = open(filepath, 'r').read()
        return (file_info, file_content)
