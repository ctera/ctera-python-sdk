from unittest import mock
import munch

from cterasdk.core import buckets, portals
from cterasdk.core.types import AmazonS3
from cterasdk import exceptions
from cterasdk.common import Object
from tests.ut.core.admin import base_admin


class TestCoreBuckets(base_admin.BaseCoreTest):

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
        ret = buckets.Buckets(self._global_admin).get(self._bucket_name)
        self._global_admin.api.get_multi.assert_called_once_with(f'/locations/{self._bucket_name}', mock.ANY)
        expected_include = ['/' + attr for attr in buckets.Buckets.default]
        actual_include = self._global_admin.api.get_multi.call_args[0][1]
        self._assert_equal_objects(actual_include, expected_include)
        self.assertEqual(ret.name, self._bucket_name)

    def test_get_bucket_not_found(self):
        get_multi_response = munch.Munch({'name': None})
        self._init_global_admin(get_multi_response=get_multi_response)
        with self.assertRaises(exceptions.CTERAException) as error:
            buckets.Buckets(self._global_admin).get(self._bucket_name)
        ref = f'/locations/{self._bucket_name}'
        self._global_admin.api.get_multi.assert_called_once_with(ref, mock.ANY)
        self.assertEqual(f'Object not found: {ref}', str(error.exception))

    def test_add_bucket(self):
        add_response = 'Success'
        get_multi_response = munch.Munch({'name': self._tenant_name, 'baseObjectRef': self._tenant_base_object_ref})
        self._init_global_admin(get_multi_response=get_multi_response, add_response=add_response)
        bucket = AmazonS3(self._bucket_name, self._access_key, self._secret_key)
        ret = buckets.Buckets(self._global_admin).add(self._bucket_name, bucket, read_only=True, dedicated_to=self._tenant_name)
        self._global_admin.api.get_multi.assert_called_once_with(f'/portals/{self._tenant_name}', mock.ANY)
        expected_include = ['/' + attr for attr in portals.Portals.default + ['baseObjectRef']]
        actual_include = self._global_admin.api.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self._global_admin.api.add.assert_called_once_with('/locations', mock.ANY)
        expected_param = TestCoreBuckets._customize_bucket(bucket.to_server_object(), name=self._bucket_name,
                                                           readOnly=True, dedicated=True,
                                                           dedicatedPortal=self._tenant_base_object_ref, trustAllCertificates=False)
        actual_param = self._global_admin.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_modify_bucket_name_ro_remove_dedication(self):
        get_response = munch.Munch({'name': self._bucket_name})
        self._init_global_admin(get_response=get_response)
        buckets.Buckets(self._global_admin).modify(self._bucket_name, self._bucket_new_name, read_only=True, dedicated_to=False)
        self._global_admin.api.get.assert_called_once_with(f'/locations/{self._bucket_name}')
        self._global_admin.api.put.assert_called_once_with(f'/locations/{self._bucket_name}', mock.ANY)
        expected_param = TestCoreBuckets._get_bucket_param(name=self._bucket_new_name, readOnly=True, dedicated=False, dedicatedPortal=None)
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_bucket_value_error(self):
        self._init_global_admin(get_response=None)
        with self.assertRaises(ValueError):
            buckets.Buckets(self._global_admin).modify(self._bucket_name, dedicated_to=True)

    def test_modify_tenant_dedication(self):
        put_response = 'Success'
        get_response = munch.Munch({})
        get_multi_response = munch.Munch({'name': self._tenant_name, 'baseObjectRef': self._tenant_base_object_ref})
        self._init_global_admin(get_response=get_response, get_multi_response=get_multi_response, put_response=put_response)
        ret = buckets.Buckets(self._global_admin).modify(self._bucket_name, dedicated_to=self._tenant_name)
        self._global_admin.api.put.assert_called_once_with(f'/locations/{self._bucket_name}', mock.ANY)
        expected_param = TestCoreBuckets._get_bucket_param(dedicated=True, dedicatedPortal=self._tenant_base_object_ref)
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_modify_bucket_not_found(self):
        self._global_admin.api.get = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            buckets.Buckets(self._global_admin).modify(self._bucket_name)
        self.assertEqual(f'Bucket not found: /locations/{self._bucket_name}', str(error.exception))

    @staticmethod
    def _get_bucket_param(**kwargs):
        param = Object()
        for key, value in kwargs.items():
            setattr(param, key, value)
        return param

    @staticmethod
    def _customize_bucket(bucket, **kwargs):
        for key, value in kwargs.items():
            setattr(bucket, key, value)
        return bucket

    def test_delete_bucket(self):
        delete_response = 'Success'
        self._init_global_admin(delete_response=delete_response)
        ret = buckets.Buckets(self._global_admin).delete(self._bucket_name)
        self._global_admin.api.delete.assert_called_once_with(f'/locations/{self._bucket_name}')
        self.assertEqual(ret, delete_response)

    def test_change_bucket_mode(self):
        for ro in [True, False]:
            put_response = 'Success'
            self._init_global_admin(put_response=put_response)
            ret = None
            if ro:
                ret = buckets.Buckets(self._global_admin).read_only(self._bucket_name)
            else:
                ret = buckets.Buckets(self._global_admin).read_write(self._bucket_name)
            self._global_admin.api.put.assert_called_once_with(f'/locations/{self._bucket_name}/readOnly', ro)
            self.assertEqual(ret, put_response)

    def test_list_buckets(self):
        with mock.patch("cterasdk.core.buckets.query.iterator") as query_iterator_mock:
            buckets.Buckets(self._global_admin).list_buckets()
            query_iterator_mock.assert_called_once_with(self._global_admin, '/locations', mock.ANY)
            expected_query_params = base_admin.BaseCoreTest._create_query_params(  # pylint: disable=protected-access
                include=buckets.Buckets.default,
                start_from=0,
                count_limit=50
            )
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)
