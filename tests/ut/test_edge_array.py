from unittest import mock

from cterasdk import exception
from cterasdk.edge import array
from cterasdk.edge.enum import RAIDLevel
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeArray(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._array_name = 'array'
        self._array_level = RAIDLevel.JBOD
        self._array_members = ['SATA-%s' % i for i in range(1, 9)]

    def test_get_all_arrays(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = array.Array(self._filer).get()
        self._filer.get.assert_called_once_with('/config/storage/arrays')
        self.assertEqual(ret, get_response)

    def test_get_array(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = array.Array(self._filer).get(self._array_name)
        self._filer.get.assert_called_once_with('/config/storage/arrays/' + self._array_name)
        self.assertEqual(ret, get_response)

    def test_add_array_success(self):
        add_response = 'Success'
        self._init_filer(add_response=add_response)
        ret = array.Array(self._filer).add(self._array_name, self._array_level, self._array_members)
        self._filer.add.assert_called_once_with('/config/storage/arrays', mock.ANY)

        expected_param = self._get_array_object()
        actual_param = self._filer.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, add_response)

    def test_add_array_failure(self):
        expected_exception = exception.CTERAException()
        self._filer.add = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            array.Array(self._filer).add(self._array_name, self._array_level, self._array_members)
        self.assertEqual('Storage array creation failed.', error.exception.message)

    def test_delete_array_success(self):
        delete_response = 'Success'
        self._init_filer(delete_response=delete_response)
        ret = array.Array(self._filer).delete(self._array_name)
        self._filer.delete.assert_called_once_with('/config/storage/arrays/' + self._array_name)
        self.assertEqual(ret, delete_response)

    def test_delete_array_failure(self):
        expected_exception = exception.CTERAException()
        self._filer.delete = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            array.Array(self._filer).delete(self._array_name)
        self.assertEqual('Storage array deletion failed.', error.exception.message)

    def test_delete_all(self):
        self.patch_call("cterasdk.edge.array.Array.delete")
        arrays = self._get_arrays_param()
        self._init_filer(get_response=arrays)
        array.Array(self._filer).delete_all()
        self._filer.get.assert_called_once_with('/config/storage/arrays')

    def _get_array_object(self):
        array_param = Object()
        array_param.name = self._array_name
        array_param.level = self._array_level
        array_param.members = self._array_members
        return array_param

    def _get_arrays_param(self):
        array_param = Object()
        array_param.name = self._array_name
        arrays = [array_param]
        return arrays
