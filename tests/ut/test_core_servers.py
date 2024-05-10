# pylint: disable=protected-access
from unittest import mock

import munch
from cterasdk.common import Object
from cterasdk.core import servers
from cterasdk import exceptions
from tests.ut import base_core


class TestCoreServers(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._server = 'ctera'
        self._task_id = 12345
        self._task_name = 'Zones Synchronizer'
        self._task_start_time = '2022-05-06T10:42:00'
        self._task_end_time = self._task_start_time
        self._task_elapsed_time = 12345
        self._task_status = 'success'
        self._task_message = 'Updated 12345 templates successfully'
        self._task_ref = f'servers/{self._server}/bgTasks/{self._task_id}'

    def test_list_servers_default_attrs(self):
        with mock.patch("cterasdk.core.servers.query.iterator") as query_iterator_mock:
            servers.Servers(self._global_admin).list_servers()
            query_iterator_mock.assert_called_once_with(self._global_admin, '/servers', mock.ANY)
            expected_query_params = base_core.BaseCoreTest._create_query_params(include=servers.Servers.default,
                                                                                start_from=0, count_limit=50)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_get_server_background_tasks(self):
        self._init_global_admin(get_response=[TestCoreServers._create_task_object(id=self._task_id,
                                                                                  name=self._task_name,
                                                                                  startTime=self._task_start_time,
                                                                                  endTime=self._task_end_time,
                                                                                  elapsedTime=self._task_elapsed_time,
                                                                                  status=self._task_status,
                                                                                  progstring=self._task_message
                                                                                  )])
        ret = servers.Servers(self._global_admin).tasks.background(self._server)
        self._global_admin.api.get.assert_called_once_with(f'/servers/{self._server}/bgTasks')
        self.assertEqual(ret[0].ref, self._task_ref)

    def test_get_server_scheduled_tasks(self):
        self._init_global_admin(get_response=[TestCoreServers._create_task_object(id=self._task_id,
                                                                                  name=self._task_name,
                                                                                  startTime=self._task_start_time
                                                                                  )])
        servers.Servers(self._global_admin).tasks.scheduled(self._server)
        self._global_admin.api.get.assert_called_once_with(f'/servers/{self._server}/schedTasks')

    def test_get_servers_success(self):
        get_multi_response = munch.Munch({'name': self._server})
        self._init_global_admin(get_multi_response=get_multi_response)
        ret = servers.Servers(self._global_admin).get(self._server)
        self._global_admin.api.get_multi.assert_called_once_with(f'/servers/{self._server}', mock.ANY)
        expected_include = ['/' + attr for attr in servers.Servers.default]
        actual_include = self._global_admin.api.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual(ret.name, self._server)

    def test_get_servers_failure(self):
        get_multi_response = munch.Munch({'name': None})
        self._init_global_admin(get_multi_response=get_multi_response)
        with self.assertRaises(exceptions.ObjectNotFoundException) as error:
            servers.Servers(self._global_admin).get(self._server)
        self._global_admin.api.get_multi.assert_called_once_with(f'/servers/{self._server}', mock.ANY)
        expected_include = ['/' + attr for attr in servers.Servers.default]
        actual_include = self._global_admin.api.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual('Could not find server', error.exception.message)

    def test_modify_server_not_found(self):
        self._init_global_admin()
        self._global_admin.api.get = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            servers.Servers(self._global_admin).modify(self._server)
        self._global_admin.api.get.assert_called_once_with(f'/servers/{self._server}')
        self.assertEqual('Failed to retrieve server', error.exception.message)

    def test_modify_server_update_failure(self):
        self._init_global_admin(get_response=self._server)
        self._global_admin.api.put = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            servers.Servers(self._global_admin).modify(self._server)
        self._global_admin.api.get.assert_called_once_with(f'/servers/{self._server}')
        self._global_admin.api.put.assert_called_once_with(f'/servers/{self._server}', self._server)
        self.assertEqual('Could not modify server', error.exception.message)

    @staticmethod
    def _create_task_object(**kwargs):
        param = Object()
        for key, value in kwargs.items():
            setattr(param, key, value)
        return param
