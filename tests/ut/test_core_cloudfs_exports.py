from unittest import mock
import munch

from cterasdk import Object
from cterasdk.core import cloudfs
from tests.ut import base_core


class TestCoreExports(base_core.BaseCoreTest):   # pylint: disable=too-many-public-methods

    # pylint: disable=too-many-instance-attributes
    def setUp(self):
        super().setUp()
        self._bucket_name = 'bucket'
        self._bucket_description = 'description'
        self._bucket_url = 'https://a.b.c.d'
        self._cloudfolder = 'name'
        self._cloudfolder_owner = 'owner'
        self._cloudfolder_baseObjectRef = 'objs/1'
        self._find_cloudfolder = self.patch_call('cterasdk.core.cloudfs.CloudDrives.find')
        self._find_cloudfolder.return_value = munch.Munch({'baseObjectRef': self._cloudfolder_baseObjectRef})

    def test_add_export(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = cloudfs.Exports(self._global_admin).add(self._bucket_name, self._cloudfolder, self._cloudfolder_owner)
        self._global_admin.api.add.assert_called_once_with('/buckets', mock.ANY)
        expected_param = self._get_add_bucket_param()
        actual_param = self._global_admin.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def _get_add_bucket_param(self):
        param = Object()
        param._classname = 'Bucket'  # pylint: disable=protected-access
        param.description = None
        param.name = self._bucket_name
        param.cloudDrive = self._cloudfolder_baseObjectRef
        return param
    
    def test_modify_bucket_description(self):
        get_response = munch.Munch({'name': self._bucket_name})
        put_response = 'Success'
        self._init_global_admin(get_response=get_response, put_response=put_response)
        ret = cloudfs.Exports(self._global_admin).modify(self._bucket_name, self._bucket_description)
        self._global_admin.api.get.assert_called_once_with(f'/buckets/{self._bucket_name}')
        self._global_admin.api.put.assert_called_once_with(f'/buckets/{self._bucket_name}', mock.ANY)
        actual_param = self._global_admin.api.put.call_args[0][1]
        get_response['description'] = self._bucket_description
        self._assert_equal_objects(actual_param, get_response)
        self.assertEqual(ret, put_response)

    def test_delete(self):
        delete_response = 'Success'
        self._init_global_admin(delete_response=delete_response)
        ret = cloudfs.Exports(self._global_admin).delete(self._bucket_name)
        self.assertEqual(ret, delete_response)

    def test_get_endpoint(self):
        get_response = munch.Munch({'url': self._bucket_url})
        self._init_global_admin(get_response=get_response)
        ret = cloudfs.Exports(self._global_admin).get_endpoint(self._bucket_name)
        self.assertEqual(ret, self._bucket_url)
