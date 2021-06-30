from unittest import mock

from cterasdk.common import Object
from tests.ut import base_core_services


class BaseCoreServicesFilesList(base_core_services.BaseCoreServicesTest):

    basepath = '/ServicesPortal/webdav'
    files = [['A', 'B', 'C'], ['D', 'E', 'F']]

    def setUp(self):
        super().setUp()
        self._path = 'Documents'

    def test_list_directory_str_arg(self):
        self._init_services()
        self._services.execute = mock.MagicMock(side_effect=BaseCoreServicesFilesList._fetch_resources_side_effect)
        iterator = self._services.files.ls(self._path)
        files = BaseCoreServicesFilesList.files[0] + BaseCoreServicesFilesList.files[1]
        for item in iterator:
            self.assertEqual(item.href, self._services.file_browser_base_path + '/' + files.pop(0))
        self._services.execute.assert_has_calls(
            [
                mock.call('', 'fetchResources', mock.ANY),
                mock.call('', 'fetchResources', mock.ANY)
            ]
        )
        expected_param = BaseCoreServicesFilesList._fetch_resources_param(self._path, 200)
        actual_param = self._services.execute.call_args_list[0][0][2]
        self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _fetch_resources_param(root, start):
        param = Object()
        param._classname = 'FetchResourcesParam'  # pylint: disable=protected-access
        param.root = BaseCoreServicesFilesList.basepath + '/' + root
        param.depth = 1
        param.start = start
        param.limit = 100
        return param

    @staticmethod
    def _fetch_resources_side_effect(path, name, param):
        # pylint: disable=unused-argument
        response = Object()
        response.items = []
        if param.start == 0:
            response.hasMore = True
            return BaseCoreServicesFilesList._fetch_resources_response(response, BaseCoreServicesFilesList.files[0])
        response.hasMore = False
        return BaseCoreServicesFilesList._fetch_resources_response(response, BaseCoreServicesFilesList.files[1])

    @staticmethod
    def _fetch_resources_response(response, files):
        for file in files:
            resource_info = BaseCoreServicesFilesList._create_resource_info(file)
            response.items.append(resource_info)
        return response

    @staticmethod
    def _create_resource_info(path):
        resource_info = Object()
        resource_info._classname = 'ResourceInfo'  # pylint: disable=protected-access
        resource_info.href = BaseCoreServicesFilesList.basepath + '/' + path
        return resource_info
