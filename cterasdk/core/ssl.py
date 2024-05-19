import logging
from zipfile import ZipFile

from .base_command import BaseCommand
from ..lib import FileSystem, X509Certificate, PrivateKey, TempfileServices, create_certificate_chain


class SSL(BaseCommand):
    """
    Portal SSL Certificate APIs
    """

    def __init__(self, portal):
        super().__init__(portal)
        self._filesystem = FileSystem.instance()

    def get(self):
        """
        Retrieve details of the current installed SSL certificate

        :return cterasdk.common.object.Object: An object including the SSL certificate details
        """
        logging.getLogger('cterasdk.core').info('Retrieving SSL certificate')
        response = self._core.api.get('/settings/ca')
        logging.getLogger('cterasdk.core').info('Retrieved SSL certificate')
        return response

    @property
    def thumbprint(self):
        """
        Get the SHA1 thumbprint of the Portal SSL certificate
        """
        return self.get().thumbprint

    def export(self, destination=None):
        """
        Export the Portal SSL Certificate to a ZIP archive

        :param str,optional destination:
         File destination, defaults to the default directory
        """
        directory, filename = self._filesystem.split_file_directory_with_defaults(destination, 'certificate.zip')
        logging.getLogger('cterasdk.core').info('Exporting SSL certificate.')
        handle = self._core.ctera.handle('/preview/exportCertificate')
        filepath = self._filesystem.save(directory, filename, handle)
        logging.getLogger('cterasdk.core').info('Exported SSL certificate. %s', {'filepath': filepath})
        return filepath

    def create_zip_archive(self, private_key, *certificates):
        """
        Create a ZIP archive that can be imported to CTERA Portal

        :param str private_key: The PEM-encoded private key, or a path to the PEM-encoded private key file
        :param list[str] certificates: The PEM-encoded certificates, or a list of paths of the PEM-encoded certificate files
        """
        tempdir = TempfileServices.mkdir()

        key_basename = 'private.key'
        key_object = PrivateKey.load_private_key(private_key)
        key_filepath = FileSystem.join(tempdir, key_basename)
        self._filesystem.write(key_filepath, key_object.pem_data)

        cert_basename = 'certificate'
        certificates = [X509Certificate.load_certificate(certificate) for certificate in certificates]
        certificate_chain = create_certificate_chain(*certificates)

        certificate_chain_zip_archive = None
        if certificate_chain:
            certificate_chain_zip_archive = FileSystem.join(tempdir, f'{cert_basename}.zip')
            with ZipFile(certificate_chain_zip_archive, 'w') as zip_archive:
                zip_archive.write(key_filepath, key_basename)
                for idx, certificate in enumerate(certificate_chain):
                    filename = f'{cert_basename}{idx if idx > 0 else ""}.crt'
                    filepath = FileSystem.join(tempdir, filename)
                    self._filesystem.write(filepath, certificate.pem_data)
                    zip_archive.write(filepath, filename)

        return certificate_chain_zip_archive

    def import_from_zip(self, zipfile):
        """
        Import an SSL Certificate to CTERA Portal from a ZIP archive

        :param str zipfile: A zip archive including the private key and SSL certificate chain
        """
        return self._import_certificate(zipfile)

    def import_from_chain(self, private_key, *certificates):
        """
        Import an SSL Certificate to CTERA Portal from a chain

        :param str private_key: The PEM-encoded private key, or a path to the PEM-encoded private key file
        :param list[str] certificates: The PEM-encoded certificates, or a list of paths of the PEM-encoded certificate files
        """
        zipflie = self.create_zip_archive(private_key, *certificates)
        return self.import_from_zip(zipflie)

    def _import_certificate(self, zipfile):
        self._filesystem.get_local_file_info(zipfile)
        logging.getLogger('cterasdk.core').info('Uploading SSL certificate.')
        with open(zipfile, 'rb') as fd:
            response = self._core.api.form_data(
                '/settings/importCertificate',
                dict(
                    name='upload',
                    certificate=fd
                )
            )
            if not isinstance(response, str):
                logging.getLogger('cterasdk.core').error('Failed uploading SSL certificate. %s', {'reason': response.msg})
            logging.getLogger('cterasdk.core').info('Uploaded SSL certificate.')
            self._core.startup.wait()
