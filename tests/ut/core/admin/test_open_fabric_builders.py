import unittest

from cterasdk.core import fusion_direct
from cterasdk.core.enum import OpenFabricStorageMode


class TestOpenFabricBuilders(unittest.TestCase):

    def test_secret_unchanged_sentinel(self):
        self.assertEqual(
            fusion_direct.FUSION_DIRECT_SECRET_KEY_UNCHANGED,
            "*****DON'T CHANGE*****",
        )

    def test_s3_data_storage_defaults(self):
        b = fusion_direct.OpenFabricS3DataStorageBuilder(
            'my-bucket', 'ak', 'sk', 'https://s3.example.com',
        ).build()
        self.assertEqual(b._classname, 'OpenFabricS3DataStorage')  # pylint: disable=protected-access
        self.assertEqual(b.storage, fusion_direct.DEFAULT_FUSION_DIRECT_S3_STORAGE)
        self.assertEqual(b.bucket, 'my-bucket')
        self.assertEqual(b.accessKey, 'ak')
        self.assertEqual(b.secretKey, 'sk')
        self.assertEqual(b.endPoint, 'https://s3.example.com')
        self.assertTrue(b.useHttps)
        self.assertFalse(b.trustAllCertificates)
        self.assertFalse(b.usePathStyleAddressing)
        self.assertFalse(b.metadataTags)

    def test_s3_data_storage_optional_fields(self):
        b = fusion_direct.OpenFabricS3DataStorageBuilder(
            'b', 'ak', 'sk', 'http://minio:9000',
            storage='MinIOS3',
            use_https=False,
            region='us-west-1',
            trust_all_certificates=True,
            use_path_style_addressing=True,
            sqs_url='https://sqs.example.com/queue',
            metadata_tags=True,
        ).build()
        self.assertEqual(b.storage, 'MinIOS3')
        self.assertFalse(b.useHttps)
        self.assertEqual(b.region, 'us-west-1')
        self.assertTrue(b.trustAllCertificates)
        self.assertTrue(b.usePathStyleAddressing)
        self.assertEqual(b.sqsUrl, 'https://sqs.example.com/queue')
        self.assertTrue(b.metadataTags)

    def test_open_fabric_settings_default_mode(self):
        data = fusion_direct.OpenFabricS3DataStorageBuilder('b', 'ak', 'sk', 'https://e').build()
        s = fusion_direct.OpenFabricSettingsBuilder(data).build()
        self.assertEqual(s._classname, 'OpenFabricSettings')  # pylint: disable=protected-access
        self.assertEqual(s.storageMode, OpenFabricStorageMode.Bucket)
        self.assertIs(s.dataStorage, data)

    def test_open_fabric_settings_explicit_mode(self):
        data = fusion_direct.OpenFabricS3DataStorageBuilder('b', 'ak', 'sk', 'https://e').build()
        s = fusion_direct.OpenFabricSettingsBuilder(
            data, storage_mode=OpenFabricStorageMode.Bidirectional,
        ).build()
        self.assertEqual(s.storageMode, OpenFabricStorageMode.Bidirectional)
