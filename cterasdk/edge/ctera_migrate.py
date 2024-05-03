import logging

from .base_command import BaseCommand
from ..common import Object
from .enum import TaskType, SourceType


class CTERAMigrate(BaseCommand):
    """Edge Filer Migration Tool APIs """

    def __init__(self, edge):
        super().__init__(edge)
        self.discovery = Discovery(self)
        self.migration = Migration(self)

    def login(self):
        """
        Login to CTERA Migrate
        """
        return self._edge.migrate.login()  # pylint: disable=protected-access

    def list_shares(self, credentials):
        """
        Log in

        :param cterasdk.edge.types.HostCredentials credentials: Target host credentials
        """
        param = Object()
        param.host = credentials.host
        param.user = credentials.username
        setattr(param, 'pass', credentials.password)
        return [share.name for share in
                self._edge.migrate.post('/inventory/shares', param).shares]  # pylint: disable=protected-access

    def list_tasks(self, deleted=False):
        """
        List tasks

        :param bool,optional deleted: List deleted tasks, defaults to ``False``
        :returns: List of tasks
        :rtype: list(cterasdk.common.object.Object)
        """
        tasks = self._edge.migrate.get('/tasks/list', params={'deleted': int(deleted)}).tasks  # pylint: disable=W0212
        return [Task.from_server_object(task) for task in tasks.__dict__.values()] if tasks else []

    def delete(self, tasks):
        """
        Delete tasks

        :param list(cterasdk.common.object.Object) tasks: List of tasks
        """
        return self._delete_or_restore(tasks, 'delete')

    def restore(self, tasks):
        """
        Recover tasks

        :param list(cterasdk.common.object.Object) tasks: List of tasks
        """
        return self._delete_or_restore(tasks, 'restore')

    def _delete_or_restore(self, tasks, action):
        param = Object()
        param.task_ids = [task.id for task in tasks]
        return self._edge.migrate.post(f'/tasks/{action}', param)  # pylint: disable=protected-access

    def start(self, task):
        """
        Start a task

        :param cterasdk.common.object.Object task: Task object
        """
        return self._update_task(task, 'enable')

    def stop(self, task):
        """
        Stop a task

        :param cterasdk.common.object.Object task: Task object
        """
        return self._update_task(task, 'disable')

    def _update_task(self, task, action):
        """
        Enable or disable a task
        """
        param = Object()
        param.task_id = task.id
        return self._edge.migrate.post(f'/tasks/{action}', param)  # pylint: disable=protected-access

    def details(self, task):
        """
        Get task details
        """
        response = self._edge.migrate.get('/tasks/history', params={'id': task.id})  # pylint: disable=protected-access
        if response.history:
            return Jobs(response.history)
        logging.getLogger('cterasdk.edge').error('Task not found. %s', {'task_id': task.id})
        return None

    def results(self, task):
        if task.type == 'discovery':
            return self._edge.migrate.get('/discovery/results',  # pylint: disable=protected-access
                                          params={'id': task.id}).discovery
        if task.type == 'migration':
            return self._edge.migrate.get('/migration/results',  # pylint: disable=protected-access
                                          params={'id': task.id}).migration
        logging.getLogger('cterasdk.edge').error('Could not determine task type. %s', {'id': task.id, 'type': task.type, 'name': task.name})
        return None


class Jobs:
    """Class representing task jobs"""

    def __init__(self, jobs):
        self._all = jobs

    @property
    def latest(self):
        """
        Get the latest job of a task
        """
        if self._all:
            return self._all[0]
        return None

    @property
    def all(self):
        """
        Get all jobs of a task
        """
        return self._all


class TaskManager:
    """Class representing a migration tool task"""

    def __init__(self, ctera_migrate):
        self._ctera_migrate = ctera_migrate

    @staticmethod
    def _create_add_parameter(name, credentials, shares, auto_start=False, notes=None):
        param = Object()
        param.name = name
        param.host = credentials.host
        param.user = credentials.username
        setattr(param, 'pass', credentials.password)
        param.shares = []
        if credentials.host_type:
            param.host_type = credentials.host_type
        for share in shares:
            share_param = Object()
            share_param.src = share
            share_param.dst = share
            param.shares.append(share_param)
        param.start = auto_start
        param.notes = notes
        return param

    def _add(self, param):
        task = self._ctera_migrate._edge.migrate.post('/tasks/create', param)  # pylint: disable=protected-access
        return Task(task.task_id, int(task.type), task.name)


class Discovery(TaskManager):

    def list_tasks(self, deleted=False):
        return [task for task in self._ctera_migrate.list_tasks(deleted) if task.type == 'discovery']  # pylint: disable=protected-access

    def add(self, name, credentials, shares, auto_start=False, log_every_file=False, notes=None):
        """
        Create a discovery task

        :param str name: Task name
        :param cterasdk.edge.types.HostCredentials credentials: Target host credentials
        :param bool,optional auto_start: Start task after creation, defaults to ``False``
        :param bool,optional log_every_file: Log every file, defaults to ``False``
        :param str,optional notes: Task notes

        :returns: Task
        :rtype: cterasdk.common.object.Object
        """
        param = TaskManager._create_add_parameter(name, credentials, shares, auto_start, notes)
        param.type = TaskType.Discovery
        param.discovery_log_files = int(log_every_file)
        return self._add(param)

    def update(self, task, name=None, notes=None):
        """
        Update a discovery task

        :param str,optional name: Task name
        :param str,optional notes: Task notes
        """
        param = Object()
        param.task_id = task.id
        if name:
            param.name = name
        if notes:
            param.notes = notes
        return self._ctera_migrate._edge.migrate.post('/tasks/update', param)  # pylint: disable=protected-access


class Migration(TaskManager):

    def list_tasks(self, deleted=False):
        return [task for task in self._ctera_migrate.list_tasks(deleted) if task.type == 'migration']  # pylint: disable=protected-access

    def add(self, name, credentials, shares, auto_start=False, access_time=None,  # pylint: disable=too-many-arguments
            winacls=True, cloud_folder=None, create_cloud_folder_per_share=False,
            compute_checksum=False, exclude=None, include=None, notes=None):
        """
        Create a discovery task

        :param str name: Task name
        :param cterasdk.edge.types.HostCredentials credentials: Target host credentials
        :param bool,optional auto_start: Start task after creation, defaults to ``False``
        :param bool,optional access_time: Copy last access time, defaults to ``None``
        :param bool,optional winacls: Copy NTFS ACL's, defaults to ``True``
        :param str,optional cloud_folder: Target cloud folder, if ``create_cloud_folder_per_share`` was set to ``True`` then
         this attribute serves as the cloud folder name prefix
        :param bool,optional create_cloud_folder_per_share: Create cloud folder per share, defaults to ``False``
        :param bool,optional compute_checksum: Validate and report checksums post-migration, defaults to ``False``
        :param list(str),optional exclude: List of patterns to exclude, defaults to ``None``
        :param list(str),optional include: List of patterns to include, defaults to ``None``
        :param str,optional notes: Task notes

        :returns: Task
        :rtype: cterasdk.common.object.Object
        """
        param = TaskManager._create_add_parameter(name, credentials, shares, auto_start, notes)
        param.type = TaskType.Migration
        param.ntacl = int(winacls)
        param.calc_write_checksum = int(compute_checksum)
        param.cf = cloud_folder
        param.cf_per_share = int(create_cloud_folder_per_share)
        if access_time:
            param.atimes = int(access_time)
        if exclude:
            param.excludes = ':'.join(exclude)
        if include:
            param.excludes = ':'.join(include)
        return self._add(param)


class Task(Object):
    """Class representing a migration tool task"""

    def __init__(self, task_id, task_type, name, created_at=None, source=None, source_type=None, last_status=None, shares=None, notes=None):
        self.id = task_id
        self.type = {v: k for k, v in TaskType.__dict__.items() if not k.startswith('_')}.get(task_type).lower()
        self.name = name
        if created_at:
            self.created_at = created_at
        if source:
            self.source = source
        if source_type:
            sources = {v: k for k, v in SourceType.__dict__.items() if not k.startswith('_')}
            self.source_type = sources.get(source_type, None) if source_type else 'other'
        if last_status:
            self.last_status = last_status
        if shares:
            self.shares = [share.src for share in shares]
        if notes:
            self.notes = notes

    @staticmethod
    def from_server_object(server_object):
        parameters = dict(
            task_id=server_object.task_id,
            task_type=server_object.type,
            name=server_object.name,
            created_at=server_object.created_time,
            source=server_object.host,
            source_type=server_object.host_type,
            last_status=server_object.status_text.lower(),
            shares=server_object.shares,
            notes=server_object.notes
        )
        if server_object.type == TaskType.Discovery:
            parameters.update(dict(
                log_every_file=bool(server_object.discovery_log_files)
            ))
            return DiscoveryTask(**parameters)
        if server_object.type == TaskType.Migration:
            parameters.update(dict(
                winacls=bool(server_object.ntacl),
                cloud_folder=server_object.cf,
                create_cloud_folder_per_share=server_object.cf_per_share,
                compute_checksum=bool(server_object.calc_write_checksum),
                exclude=server_object.excludes,
                include=server_object.includes,
                access_time=getattr(server_object, 'atimes', None),
                schedule=f'{server_object.schedule_date.replace("/", "-")} {server_object.schedule_time}'
                         if server_object.schedule_date else None
            ))

            throttling_rule = getattr(server_object, 'bwlimit', None)
            throttling = None
            if throttling_rule:
                throttling = Object()
                throttling.kbps = throttling_rule.limit
                throttling.start = getattr(throttling_rule, 'from', None)
                throttling.end = getattr(throttling_rule, 'to', None)
            parameters['throttling'] = throttling

            return MigrationTask(**parameters)
        return None


class DiscoveryTask(Task):
    """Class representing a migration tool discovery task"""

    def __init__(self, task_id, task_type, name, created_at, source, source_type,  # pylint: disable=too-many-arguments
                 last_status, shares, notes, log_every_file):
        super().__init__(task_id, task_type, name, created_at, source, source_type, last_status, shares, notes)
        self.log_every_file = log_every_file


class MigrationTask(Task):
    """Class representing a migration tool migration task"""

    def __init__(self, task_id, task_type, name, created_at, source, source_type,  # pylint: disable=too-many-arguments, too-many-locals
                 last_status, shares, notes, winacls, cloud_folder, create_cloud_folder_per_share,
                 compute_checksum, exclude, include, access_time, schedule, throttling):
        super().__init__(task_id, task_type, name, created_at, source, source_type, last_status, shares, notes)
        self.winacls = winacls
        self.cloud_folder = cloud_folder
        self.create_cloud_folder_per_share = create_cloud_folder_per_share
        self.compute_checksum = compute_checksum
        self.exclude = exclude
        self.include = include
        self.access_time = access_time
        self.schedule = schedule
        self.throttling = throttling
