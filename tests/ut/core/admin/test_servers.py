# pylint: disable=protected-access
from unittest import mock

import munch
from cterasdk.common import Object
from cterasdk.core import servers
from cterasdk.core.types import AmazonS3
from cterasdk import exceptions
from tests.ut.core.admin import base_admin


class TestCoreServers(base_admin.BaseCoreTest):

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
            expected_query_params = base_admin.BaseCoreTest._create_query_params(include=servers.Servers.default,
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
        self.assertEqual(f'Object not found: /servers/{self._server}', str(error.exception))

    def test_modify_server_not_found(self):
        self._init_global_admin()
        self._global_admin.api.get = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            servers.Servers(self._global_admin).modify(self._server)
        self._global_admin.api.get.assert_called_once_with(f'/servers/{self._server}')
        self.assertEqual(f'Server not found: /servers/{self._server}', str(error.exception))

    def test_modify_server_update_failure(self):
        self._init_global_admin(get_response=self._server)
        self._global_admin.api.put = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            servers.Servers(self._global_admin).modify(self._server)
        ref = f'/servers/{self._server}'
        self._global_admin.api.get.assert_called_once_with(ref)
        self._global_admin.api.put.assert_called_once_with(f'/servers/{self._server}', self._server)
        self.assertEqual(f'Server modification failed: {ref}', str(error.exception))

    def test_modify_success(self):
        new_server_name = 'server1'
        public_ip = '192.168.90.1'
        replica_base_object_ref = 'objs/server'
        get_multi_response = munch.Munch({'name': self._server, 'baseObjectRef': replica_base_object_ref})
        put_response = 'Success'
        self._init_global_admin(get_response=munch.Munch({'name': self._server}), get_multi_response=get_multi_response,
                                put_response=put_response)
        ret = servers.Servers(self._global_admin).modify(self._server, new_server_name, True, True, True, public_ip, False, self._server)
        expected_param = TestCoreServers._create_server_object(new_server_name, True, True,
                                                               True, public_ip, False, True, replica_base_object_ref)
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_system_database(self):
        with mock.patch("cterasdk.core.servers.query.run") as query_mock:
            query_mock.return_value = munch.Munch({
                'objects': [munch.Munch({'mainDB': True})]
            })
            server = servers.Servers(self._global_admin).system_database
            expected_query_params = base_admin.BaseCoreTest._create_query_params(start_from=0, count_limit=50, filters=[
                munch.Munch({
                    'field': 'mainDB',
                    'restriction': 'eq',
                    '_classname': 'BooleanFilter',
                    'value': True
                })
            ])
            actual_query_params = query_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)
            self.assertEqual(server.mainDB, True)

    def test_enable_server_backup(self):
        self._init_global_admin()
        server_name = 'server'
        with mock.patch("cterasdk.core.servers.Servers.system_database", new_callable=mock.PropertyMock) as query_mock:
            query_mock.return_value = munch.Munch({'name': server_name, 'backupToBucket': None})
            bucket, access, secret, endpoint = 'bucket-name', 'access', 'secret', 'www.endpoint.com'
            bucket = AmazonS3(bucket, access, secret, endpoint, True, verify_ssl=False)
            servers.Servers(self._global_admin).backup.enable(bucket, 60)
            self._global_admin.api.put.assert_called_once_with(f'/servers/{server_name}', mock.ANY)
            actual_param = self._global_admin.api.put.call_args[0][1]
            expected_param = munch.Munch({
                'enabled': True,
                'exportSchedulePeriod': 60,
                'details': TestCoreServers._create_database_backup_server_object(bucket)
            })
            self._assert_equal_objects(actual_param.backupToBucket, expected_param)

    def test_enable_server_backup_path_style(self):
        from cterasdk.core.types import GenericS3
        self._init_global_admin()
        server_name = 'server'
        with mock.patch("cterasdk.core.servers.Servers.system_database", new_callable=mock.PropertyMock) as query_mock:
            query_mock.return_value = munch.Munch({'name': server_name, 'backupToBucket': None})
            bucket = GenericS3('portal-backup', 'access', 'secret', 'os.example.com', https=True, verify_ssl=True, path_style=True)
            servers.Servers(self._global_admin).backup.enable(bucket, 5)
            self._global_admin.api.put.assert_called_once_with(f'/servers/{server_name}', mock.ANY)
            actual_param = self._global_admin.api.put.call_args[0][1]
            expected_param = munch.Munch({
                'enabled': True,
                'exportSchedulePeriod': 5,
                'details': TestCoreServers._create_database_backup_server_object(bucket)
            })
            self._assert_equal_objects(actual_param.backupToBucket, expected_param)

    @staticmethod
    def _create_database_backup_server_object(bucket):
        return munch.Munch({
            'storage': bucket.driver,
            'bucket': bucket.bucket,
            'accessKey': bucket.access_key,
            'secretKey': bucket.secret_key,
            'endPoint': bucket.endpoint,
            'useHttps': bucket.https,
            'trustAllCertificates': bucket.trust_all_certificates,
            'masterHost': None,
            'usePathStyleAddressing': bucket.path_style
        })

    def test_disable_server_backup(self):
        self._init_global_admin()
        server_name = 'server'
        with mock.patch("cterasdk.core.servers.Servers.system_database", new_callable=mock.PropertyMock) as query_mock:
            query_mock.return_value = munch.Munch({'name': server_name, 'backupToBucket': munch.Munch({'enabled': True})})
            servers.Servers(self._global_admin).backup.disable()
            self._global_admin.api.put.assert_called_once_with(f'/servers/{server_name}', mock.ANY)
            actual_param = self._global_admin.api.put.call_args[0][1]
            self._assert_equal_objects(actual_param.backupToBucket.enabled, False)

    def test_get_server_backup(self):
        self._init_global_admin()
        backup_config = munch.Munch({'enabled': True, 'exportSchedulePeriod': 5, 'status': 'Connected'})
        with mock.patch("cterasdk.core.servers.Servers.system_database", new_callable=mock.PropertyMock) as query_mock:
            query_mock.return_value = munch.Munch({'backupToBucket': backup_config})
            ret = servers.Servers(self._global_admin).backup.get()
            self._assert_equal_objects(ret, backup_config)

    def test_server_backup_status(self):
        self._init_global_admin()
        with mock.patch("cterasdk.core.servers.Servers.system_database", new_callable=mock.PropertyMock) as query_mock:
            query_mock.return_value = munch.Munch({'backupToBucket': munch.Munch({'status': 'Connected'})})
            ret = servers.Servers(self._global_admin).backup.connected()
            self.assertEqual(ret, True)

    @staticmethod
    def _create_server_object(name=None, app=None, preview=None, enable_public_ip=None,
                              public_ip=None, allow_user_login=None, enable_replication=None, replica_of=None):
        server = Object()
        if enable_replication is True and replica_of is not None:
            server.replicationSettings = Object()
            server.replicationSettings._classname = 'ServerReplicationSettings'  # pylint: disable=protected-access
            server.replicationSettings.replicationOf = replica_of
        if enable_replication is False:
            server.replicationSettings = None
        if name is not None:
            server.name = name
        if app is not None:
            server.isApplicationServer = app
        if preview is not None:
            server.renderingServer = preview
        if enable_public_ip is True and public_ip is not None:
            server.publicIpaddr = public_ip
        elif enable_public_ip is False:
            server.publicIpaddr = None
        if allow_user_login is not None:
            server.allowUserLogin = allow_user_login
        return server

    @staticmethod
    def _create_task_object(**kwargs):
        param = Object()
        for key, value in kwargs.items():
            setattr(param, key, value)
        return param
