import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from cterasdk.core.enum import DatabaseMode, ExternalDbAuthMethod
from cterasdk.core.external_database import (
    auth_method_to_schema_auth_mode,
    build_external_database_config,
    resolve_init_database_configuration,
)
from cterasdk.exceptions import CTERAException
from tests.ut import base


class TestExternalDatabase(base.BaseTest):

    @staticmethod
    def _generate_self_signed_material():
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'test')])
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=1))
            .sign(key, hashes.SHA256())
        )
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
        key_pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        ).decode('utf-8')
        return cert_pem, key_pem

    def test_auth_method_to_schema_auth_mode(self):
        self.assertEqual(auth_method_to_schema_auth_mode(ExternalDbAuthMethod.Credentials), 'Credentials')
        self.assertEqual(auth_method_to_schema_auth_mode(ExternalDbAuthMethod.Certificate), 'Cert')
        self.assertEqual(auth_method_to_schema_auth_mode(ExternalDbAuthMethod.Token), 'Token')

    def test_resolve_embedded_returns_no_config(self):
        mode, config = resolve_init_database_configuration(database_mode=DatabaseMode.Embedded)
        self.assertEqual(mode, DatabaseMode.Embedded)
        self.assertIsNone(config)

    def test_resolve_embedded_rejects_external_fields(self):
        with self.assertRaises(CTERAException):
            resolve_init_database_configuration(
                database_mode=DatabaseMode.Embedded,
                ext_db_host='db.example.com',
            )

    def test_resolve_external_requires_host_and_user(self):
        with self.assertRaises(CTERAException):
            resolve_init_database_configuration(
                database_mode=DatabaseMode.External,
                ext_db_user='app',
                ext_db_password='secret',
                ext_db_ssl_mode='require',
            )

    def test_resolve_external_rejects_disable_ssl(self):
        with self.assertRaises(CTERAException):
            resolve_init_database_configuration(
                database_mode=DatabaseMode.External,
                ext_db_host='db.example.com',
                ext_db_user='app',
                ext_db_password='secret',
                ext_db_ssl_mode='disable',
            )

    def test_resolve_external_rejects_invalid_ssl_mode(self):
        with self.assertRaises(CTERAException):
            resolve_init_database_configuration(
                database_mode=DatabaseMode.External,
                ext_db_host='db.example.com',
                ext_db_user='app',
                ext_db_password='secret',
                ext_db_ssl_mode='prefer',
            )

    def test_build_external_database_config_preserves_ca_bundle(self):
        cert_pem, _ = self._generate_self_signed_material()
        other_pem, _ = self._generate_self_signed_material()
        bundle = cert_pem + other_pem
        config = build_external_database_config(
            host='db.example.com',
            username='app',
            password='secret',
            ssl_mode='verify-full',
            ssl_ca_cert=bundle,
        )
        self.assertEqual(config.sslCaCert.count('BEGIN CERTIFICATE'), 2)

    def test_resolve_external_credentials_builds_config(self):
        mode, config = resolve_init_database_configuration(
            database_mode=DatabaseMode.External,
            ext_db_host='db.example.com',
            ext_db_port=5433,
            ext_db_name='portal',
            ext_db_user='app',
            ext_db_password='secret',
            ext_db_ssl_mode='require',
        )
        self.assertEqual(mode, DatabaseMode.External)
        self.assertEqual(config.host, 'db.example.com')
        self.assertEqual(config.port, 5433)
        self.assertEqual(config.databaseName, 'portal')
        self.assertEqual(config.username, 'app')
        self.assertEqual(config.password, 'secret')
        self.assertEqual(config.sslMode, 'require')
        self.assertEqual(config.authMode, 'Credentials')

    def test_build_external_database_config_with_certificate_material(self):
        cert_pem, key_pem = self._generate_self_signed_material()
        config = build_external_database_config(
            host='db.example.com',
            username='app',
            password=None,
            ssl_mode='verify-full',
            auth_method=ExternalDbAuthMethod.Certificate,
            ssl_ca_cert=cert_pem,
            ssl_client_cert=cert_pem,
            ssl_client_key=key_pem,
        )
        self.assertEqual(config.authMode, 'Cert')
        self.assertIn('BEGIN CERTIFICATE', config.sslCaCert)
        self.assertIn('BEGIN CERTIFICATE', config.authCert)
        self.assertIn('BEGIN', config.authKey)
