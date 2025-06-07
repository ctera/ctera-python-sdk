import logging
from zipfile import ZipFile

from .base_command import BaseCommand
from ..lib import X509Certificate, PrivateKey, TempfileServices, create_certificate_chain
from ..lib.storage import commonfs, synfs


logger = logging.getLogger('cterasdk.core')


class SSL(BaseCommand):
    """
    Portal SSL Certificate APIs
    """

    def get(self):
        """
        Retrieve details of the current installed SSL certificate

        :return cterasdk.common.object.Object: An object including the SSL certificate details
        """
        logger.info('Retrieving SSL certificate')
        response = self._core.api.get('/settings/ca')
        logger.info('Retrieved SSL certificate')
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
        directory, filename = commonfs.generate_file_destination(destination, 'certificate.zip')
        logger.info('Exporting SSL certificate.')
        handle = self._core.ctera.handle('/preview/exportCertificate')
        filepath = synfs.write(directory, filename, handle)
        logger.info('Exported SSL certificate. %s', {'filepath': filepath})
        return filepath

    @staticmethod
    def create_zip_archive(private_key, *certificates):
        """
        Create a ZIP archive that can be imported to CTERA Portal

        :param str private_key: The PEM-encoded private key, or a path to the PEM-encoded private key file
        :param list[str] certificates: The PEM-encoded certificates, or a list of paths of the PEM-encoded certificate files
        """
        tempdir = TempfileServices.mkdir()

        key_basename = 'private.key'
        key_object = PrivateKey.load_private_key(private_key)
        key_filepath = commonfs.join(tempdir, key_basename)
        synfs.overwrite(key_filepath, key_object.pem_data)

        cert_basename = 'certificate'
        certificates = [X509Certificate.load_certificate(certificate) for certificate in certificates]
        certificate_chain = create_certificate_chain(*certificates)

        certificate_chain_zip_archive = None
        if certificate_chain:
            certificate_chain_zip_archive = commonfs.join(tempdir, f'{cert_basename}.zip')
            with ZipFile(certificate_chain_zip_archive, 'w') as zip_archive:
                zip_archive.write(key_filepath, key_basename)
                for idx, certificate in enumerate(certificate_chain):
                    filename = f'{cert_basename}{idx if idx > 0 else ""}.crt'
                    filepath = commonfs.join(tempdir, filename)
                    synfs.overwrite(filepath, certificate.pem_data)
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
        zipflie = SSL.create_zip_archive(private_key, *certificates)
        return self.import_from_zip(zipflie)

    def _import_certificate(self, zipfile):
        commonfs.properties(zipfile)
        logger.info('Uploading SSL certificate.')
        with open(zipfile, 'rb') as fd:
            response = self._core.api.form_data(
                '/settings/importCertificate',
                dict(
                    name='upload',
                    certificate=fd
                )
            )
            if not isinstance(response, str):
                logger.error('Failed uploading SSL certificate. %s', {'reason': response.msg})
            logger.info('Uploaded SSL certificate.')
            self._core.startup.wait()
