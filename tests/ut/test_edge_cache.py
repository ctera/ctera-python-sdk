from unittest import mock

from cterasdk import exception
from cterasdk.edge import cache
from cterasdk.common import Object
from cterasdk.edge.enum import OperationMode
from tests.ut import base_edge


class TestEdgeCaching(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._display_name = None
        self._root = 'users'
        self._pin_valid_folder_path = 'users/Service Account/folder'
        self._pin_exclude_subfolder_path = 'users/Service Account/folder/excluded_folder'
        self._pin_invalid_folder_path = 'wrongpath/Service Account/folder'

    def test_enable_caching(self):
        self._init_filer()
        cache.Cache(self._filer).enable()
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/operationMode', OperationMode.CachingGateway)

    def test_disable_caching(self):
        self._init_filer()
        cache.Cache(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/operationMode', OperationMode.Disabled)

    def test_force_eviction(self):
        self._init_filer()
        cache.Cache(self._filer).force_eviction()
        self._filer.execute.assert_called_once_with('/config/cloudsync', 'forceExecuteEvictor', None)

    def test_pin_folder(self):
        get_response = self._get_dir_entry(self._root, False)
        self._init_filer(get_response=get_response)
        cache.Cache(self._filer).pin(self._pin_valid_folder_path)
        self._filer.get.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders')
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders', mock.ANY)

        expected_param = self._create_dir_tree(self._pin_valid_folder_path, True)
        actual_param = self._filer.put.call_args[0][1]
        TestEdgeCaching._remove_parent_attrs(actual_param)
        self._assert_equal_objects(expected_param, actual_param)

    def test_pin_invalid_root_directory(self):
        get_response = self._get_dir_entry(self._root, False)
        self._init_filer(get_response=get_response)
        with self.assertRaises(exception.CTERAException) as error:
            cache.Cache(self._filer).pin(self._pin_invalid_folder_path)
        self._filer.get.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders')
        self.assertEqual('Invalid root directory', error.exception.message)

    def test_pin_exclude_subfolder(self):
        get_response = self._create_dir_tree(self._pin_valid_folder_path, True)
        self._init_filer(get_response=get_response)
        cache.Cache(self._filer).pin_exclude(self._pin_exclude_subfolder_path)
        self._filer.get.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders')
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders', mock.ANY)

        expected_param = self._create_dir_tree(self._pin_valid_folder_path, True)
        descendant = self._get_dir_entry(self._pin_exclude_subfolder_path.split('/')[-1], False)
        TestEdgeCaching._add_descendant(expected_param, descendant)

        actual_param = self._filer.put.call_args[0][1]
        TestEdgeCaching._remove_parent_attrs(actual_param)
        self._assert_equal_objects(expected_param, actual_param)

    def test_remove_pin(self):
        get_response = self._create_dir_tree(self._pin_exclude_subfolder_path, True)
        self._init_filer(get_response=get_response)
        cache.Cache(self._filer).remove_pin(self._pin_exclude_subfolder_path)
        self._filer.get.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders')
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders', mock.ANY)

        expected_param = self._create_dir_tree(self._pin_valid_folder_path, False)
        actual_param = self._filer.put.call_args[0][1]
        TestEdgeCaching._remove_parent_attrs(actual_param)
        self._assert_equal_objects(expected_param, actual_param)

    def test_pin_all(self):
        get_response = self._get_dir_entry(self._root, False)
        self._init_filer(get_response=get_response)
        cache.Cache(self._filer).pin_all()
        self._filer.get.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders')
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders', mock.ANY)

        expected_param = self._get_dir_entry(self._root, True)
        actual_param = self._filer.put.call_args[0][1]
        TestEdgeCaching._remove_parent_attrs(actual_param)
        self._assert_equal_objects(expected_param, actual_param)

    def test_unpin_all(self):
        get_response = self._get_dir_entry(self._root, True)
        self._init_filer(get_response=get_response)
        cache.Cache(self._filer).unpin_all()
        self._filer.get.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders')
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/selectedFolders', mock.ANY)

        expected_param = self._get_dir_entry(self._root, False)
        actual_param = self._filer.put.call_args[0][1]
        TestEdgeCaching._remove_parent_attrs(actual_param)
        self._assert_equal_objects(expected_param, actual_param)

    def _get_dir_entry(self, name, include):
        param = Object()
        param._classname = 'DirEntry'  # pylint: disable=protected-access
        param.name = name
        param.children = None
        param.displayName = self._display_name
        param.isIncluded = include
        return param

    def _create_dir_tree(self, path, include_descendant):
        parts = path.split('/')
        descendant = self._get_dir_entry(parts.pop(), include_descendant)
        if parts:
            root_dir_entry = self._get_dir_entry(parts.pop(0), False)
            parent_dir_entry = root_dir_entry
            for part in parts:
                dir_entry = self._get_dir_entry(part, False)
                TestEdgeCaching._add_child(parent_dir_entry, dir_entry)
                parent_dir_entry = dir_entry
            TestEdgeCaching._add_child(parent_dir_entry, descendant)
            return root_dir_entry
        return descendant

    @staticmethod
    def _add_descendant(node, descendant):
        while node.children is not None:
            node = node.children[0]
        node.children = [descendant]

    @staticmethod
    def _add_child(parent, child):
        if parent.children is None:
            parent.children = []
        parent.children.append(child)

    @staticmethod
    def _remove_parent_attrs(obj):
        objects = [obj]
        while objects:
            obj = objects.pop(0)
            delattr(obj, '_parent')
            if obj.children is not None:
                for child_obj in obj.children:
                    objects.append(child_obj)
