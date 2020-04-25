import logging

from .base_command import BaseCommand
from ..lib import FileSystem


class SSL(BaseCommand):
    """ Gateway SSL APIs """

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

    def _load_cert(self, certificate, private_key, reboot=True, wait_for_reboot=False):
        logging.getLogger().info("Uploading server certificate and private key")
        server_certificate = '\n' + private_key + certificate
        response = self._gateway.put('/config/certificate', server_certificate)
        logging.getLogger().info("Uploaded server certificate and private key.")
        if reboot:
            self._gateway.power.reboot(wait_for_reboot)
        return response

    def upload_cert(self, certificate, private_key, reboot=True, wait_for_reboot=False):
        """
        Upload a server certificate

        :param str certificate: A path to the PEM-encoded server certificate file
        :param str private_key: A path to the PEM-encoded private key
        """
        file_info, cert = SSL._file_contents(certificate)
        logging.getLogger().debug(
            {'name': file_info['name'], 'size': file_info['size'], 'type': file_info['mimetype']}
        )
        file_info, pk = SSL._file_contents(private_key)
        logging.getLogger().debug(
            "Read private key file. %s", {'name': file_info['name'], 'size': file_info['size'], 'type': file_info['mimetype']}
        )
        return self._load_cert(cert, pk, reboot, wait_for_reboot)

    @staticmethod
    def _file_contents(filepath):
        file_info = FileSystem.instance().get_local_file_info(filepath)
        file_content = open(filepath, 'r').read()
        return (file_info, file_content)
