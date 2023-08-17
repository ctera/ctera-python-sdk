import munch

from cterasdk.core import buckets, portals
from cterasdk.core.types import AmazonS3
from tests.ut import base_core


class TestCoreBuckets(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._bucket_name = 'bucket'
        self._bucket_new_name = 'bucket2'
        self._access_key = 'access'
        self._secret_key = 'secret'
        self._tenant_name = 'tenant'
        self._tenant_base_object_ref = 'reference'

    def test_get_bucket_success(self):
        get_multi_response = munch.Munch({'name': self._bucket_name})
        self._init_global_admin(get_multi_response=get_multi_response)
        ret = bucket.Buckets(self._global_admin).get(self._bucket_name)
        self._global_admin.get_multi.assert_called_once_with(f'/locations/{self._bucket_name}', mock.ANY)
        expected_include = ['/' + attr for attr in buckets.Buckets.default]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self._assert_equal_objects(actual_include, expected_include)
        self.assertEqual(ret.name, self._bucket_name)

    def test_get_bucket_not_found(self):
        get_multi_response = munch.Munch({'name': None})
        self._init_global_admin(get_multi_response=get_multi_response)
        with self.assertRaises(exception.CTERAException) as error:
            bucket.Buckets(self._global_admin).get(self._bucket_name)
        self._global_admin.get_multi.assert_called_once_with(f'/locations/{self._bucket_name}', mock.ANY)
        self.assertEqual('Could not find bucket', error.exception.message)

    def test_add_bucket(self):
        add_response = 'Success'
        get_multi_response = munch.Munch({'name': self._tenant_name, 'baseObjectRef': self._tenant_base_object_ref})
        self._init_global_admin(get_multi_response=get_multi_response, add_response=add_response)
        bucket = AmazonS3(self._bucket_name, self._access_key, self._secret_key, read_only=True, dedicated_to=self._tenant_name)
        ret = bucket.Buckets(self._global_admin).add(self._bucket_name, bucket)
        self._global_admin.get_multi.assert_called_once_with(f'/portals/{self._tenant_name}', mock.ANY)
        expected_include = ['/' + attr for attr in portals.Portals.default + ['baseObjectRef']]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self._assert_equal_objects(actual_include, expected_include)
        self._global_admin.add.assert_called_once_with(f'/locations', mock.ANY)
        expected_param = self._get_bucket_param(self._bucket_name, True, True, self._tenant_base_object_ref)
        actual_param = self._global_admin.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_modify_bucket_name_ro_remove_dedication(self):
        get_multi_response = munch.Munch({'name': self._bucket_name})
        self._init_global_admin(get_multi_response=get_multi_response)
        ret = bucket.Buckets(self._global_admin).modify(self._bucket_name, self._bucket_new_name, read_only=True, dedicated_to=False)
        self._global_admin.get.assert_called_once_with(f'/locations/{self._bucket_name}')
        self._global_admin.put.assert_called_once_with(f'/locations/{self._bucket_name}', mock.ANY)
        expected_param = self._get_bucket_param(self._bucket_new_name, True, False, None)
        actual_param = self._global_admin.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_bucket_param(name=None, read_only=None, dedicated_to=None, dedicated_tenant=None):
        return munch.Munch({
            'name': name
            'readOnly': read_only,
            'dedicated': dedicated_to,
            'dedicatedPortal': dedicated_tenant
        })
        
        

    
