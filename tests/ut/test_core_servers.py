# pylint: disable=protected-access
from unittest import mock

from cterasdk.common import Object
from cterasdk.core import servers
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
                                                                                 progstring=self._task_message)])
        ret = servers.Servers(self._global_admin).tasks.background(self._server)
        self._global_admin.get.assert_called_once_with(f'/servers/{self._server}/bgTasks')
        self.assertEqual(ret[0].ref, self._task_ref)

    def test_get_server_scheduled_tasks(self):
        self._init_global_admin(get_response=[TestCoreServers._create_task_object(id=self._task_id,
                                                                                  name=self._task_name,
                                                                                  startTime=self._task_start_time
                                                                                  )])
        servers.Servers(self._global_admin).tasks.scheduled(self._server)
        self._global_admin.get.assert_called_once_with(f'/servers/{self._server}/schedTasks')

    @staticmethod
    def _create_task_object(**kwargs):
        param = Object()
        for key, value in kwargs.items():
            setattr(param, key, value)
        return param
