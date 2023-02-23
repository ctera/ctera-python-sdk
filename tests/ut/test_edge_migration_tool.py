from unittest import mock
import munch

from cterasdk.edge import migration_tool
from cterasdk.edge.enum import TaskType
from cterasdk.edge.types import HostCredentials
from tests.ut import base_edge


class TestMigrationTool(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._host = '192.168.0.1'
        self._username = 'admin'
        self._password = 'password'
        self._shares = ['public', 'ctera', 'private']
        self._jobs = [1, 2, 3]
        self._task_id = 1
        self._task_ids = [1, 2, 3]

    def test_login(self):
        self._init_ctera_migrate()
        migration_tool.MigrationTool(self._filer).login()
        self._filer._ctera_migrate.login.assert_called_once_with('/migration/rest/v1/auth/user')

    def test_list_shares(self):
        self._init_ctera_migrate(post_response=munch.Munch(dict(shares=[munch.Munch(dict(name=name)) for name in self._shares])))
        ret = migration_tool.MigrationTool(self._filer).list_shares(HostCredentials(self._host, self._username, self._password))
        self._filer._ctera_migrate.post.assert_called_once_with('/migration/rest/v1/inventory/shares', mock.ANY)
        actual_param = self._filer._ctera_migrate.post.call_args[0][1]

        expected_param = munch.Munch(host=self._host, user=self._username)
        setattr(expected_param, 'pass', self._password)
        self._assert_equal_objects(actual_param, expected_param)

        for name in self._shares:
            self.assertIn(name, ret)

    def test_list_tasks_empty_response(self):
        self._init_ctera_migrate(get_response=munch.Munch(dict(tasks=None)))
        ret = migration_tool.MigrationTool(self._filer).list_tasks()
        self._filer._ctera_migrate.get.assert_called_once_with('/migration/rest/v1/tasks/list', {'deleted': int(False)})
        self.assertEqual(ret, [])

    def test_list_tasks_with_response(self):
        tasks = munch.Munch(dict(discovery=TestMigrationTool._create_discovery_task_object(),
                                 migration=TestMigrationTool._create_migration_task_object()))
        self._init_ctera_migrate(get_response=munch.Munch(dict(tasks=tasks)))
        migration_tool.MigrationTool(self._filer).list_tasks()
        self._filer._ctera_migrate.get.assert_called_once_with('/migration/rest/v1/tasks/list', {'deleted': int(False)})

    def test_delete(self):
        self._init_ctera_migrate(post_response='Success')
        tasks = [munch.Munch(id=task_id) for task_id in self._task_ids]
        ret = migration_tool.MigrationTool(self._filer).delete(tasks)
        self._filer._ctera_migrate.post.assert_called_once_with('/migration/rest/v1/tasks/delete', mock.ANY)
        actual_param = self._filer._ctera_migrate.post.call_args[0][1]
        self._assert_equal_objects(actual_param, munch.Munch(task_ids=self._task_ids))
        self.assertEqual(ret, 'Success')

    def test_restore(self):
        self._init_ctera_migrate(post_response='Success')
        tasks = [munch.Munch(id=task_id) for task_id in self._task_ids]
        ret = migration_tool.MigrationTool(self._filer).restore(tasks)
        self._filer._ctera_migrate.post.assert_called_once_with('/migration/rest/v1/tasks/restore', mock.ANY)
        actual_param = self._filer._ctera_migrate.post.call_args[0][1]
        self._assert_equal_objects(actual_param, munch.Munch(task_ids=self._task_ids))
        self.assertEqual(ret, 'Success')

    def test_start(self):
        self._init_ctera_migrate(post_response='Success')
        ret = migration_tool.MigrationTool(self._filer).start(munch.Munch(id=self._task_id))
        self._filer._ctera_migrate.post.assert_called_once_with('/migration/rest/v1/tasks/enable', mock.ANY)
        actual_param = self._filer._ctera_migrate.post.call_args[0][1]
        self._assert_equal_objects(actual_param, munch.Munch(task_id=self._task_id))
        self.assertEqual(ret, 'Success')

    def test_stop(self):
        self._init_ctera_migrate(post_response='Success')
        ret = migration_tool.MigrationTool(self._filer).stop(munch.Munch(id=self._task_id))
        self._filer._ctera_migrate.post.assert_called_once_with('/migration/rest/v1/tasks/disable', mock.ANY)
        actual_param = self._filer._ctera_migrate.post.call_args[0][1]
        self._assert_equal_objects(actual_param, munch.Munch(task_id=self._task_id))
        self.assertEqual(ret, 'Success')

    def test_details(self):
        self._init_ctera_migrate(get_response=munch.Munch(dict(history=self._jobs)))
        jobs = migration_tool.MigrationTool(self._filer).details(munch.Munch(id=self._task_id))
        self._filer._ctera_migrate.get.assert_called_once_with('/migration/rest/v1/tasks/history', {'id': self._task_id})
        self.assertEqual(jobs.all, self._jobs)
        self.assertEqual(jobs.latest, self._jobs[0])

    def test_details_not_found(self):
        self._init_ctera_migrate(get_response=munch.Munch(dict(history=None)))
        migration_tool.MigrationTool(self._filer).details(munch.Munch(id=self._task_id))
        self._filer._ctera_migrate.get.assert_called_once_with('/migration/rest/v1/tasks/history', {'id': self._task_id})

    def test_results(self):
        self._init_ctera_migrate(get_response=munch.Munch(dict(discovery='discovery', migration='migration')))
        for i in [TaskType.Discovery, TaskType.Migration, 3]:
            ret = migration_tool.MigrationTool(self._filer).results(munch.Munch(id=i, type=i, name='task'))
            if i == TaskType.Discovery:
                self._filer._ctera_migrate.get.assert_called_with('/migration/rest/v1/discovery/results', {'id': TaskType.Discovery})
                self.assertEqual(ret, 'discovery')
            elif i == TaskType.Migration:
                self._filer._ctera_migrate.get.assert_called_with('/migration/rest/v1/migration/results', {'id': TaskType.Migration})
                self.assertEqual(ret, 'migration')
            else:
                self.assertEqual(ret, None)

    @staticmethod
    def _create_discovery_task_object():
        return TestMigrationTool._create_object(**{
            'task_id': 1, 'type': TaskType.Discovery, 'name': 'discovery', 'created_time': None, 'host': '192.168.0.1',
            'host_type': 'windowsServer', 'status_text': 'status', 'shares': [munch.Munch(dict(src='public'))],
            'notes': 'test note', 'discovery_log_files': 1
        })

    @staticmethod
    def _create_migration_task_object():
        return TestMigrationTool._create_object(**{
            'task_id': 1, 'type': TaskType.Migration, 'name': 'migration', 'created_time': None, 'host': '192.168.0.1',
            'host_type': 'windowsServer', 'status_text': 'status', 'shares': [munch.Munch(dict(src='public'))],
            'notes': 'test note', 'ntacl': 1, 'cf': 'My Files', 'cf_per_share': False, 'calc_write_checksum': True,
            'excludes': '', 'includes': '', 'atimes': True, 'schedule_date': None,
            'bwlimit': munch.Munch({'kbps': 100, 'from': 'start', 'to': 'end'})
        })

    @staticmethod
    def _create_object(**kwargs):
        param = munch.Munch()
        for key, value in kwargs.items():
            setattr(param, key, value)
        return param
