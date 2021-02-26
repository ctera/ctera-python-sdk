import logging

from ..lib import track, ErrorStatus
from .enum import Mode, SyncStatus, Acl
from .types import FilterBackupSet, FileExclusionBuilder
from .base_command import BaseCommand
from ..common import ThrottlingRule


class Sync(BaseCommand):
    """
    Edge Filer Cloud Sync APIs

    :ivar cterasdk.edge.sync.CloudSyncBandwidthThrottling throttling: Object holding the Edge Filer's bandwidth throttling APIs
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.throttling = CloudSyncBandwidthThrottling(self._gateway)

    def get_status(self):
        """ Retrieve the Cloud Sync status """
        return self._gateway.get('/proc/cloudsync/serviceStatus')

    def is_disabled(self):
        """ Check if Cloud Sync is disabled """
        return self._gateway.get('/config/cloudsync/mode') == Mode.Disabled

    def is_enabled(self):
        """ Check if Cloud Sync is enabled """
        return self._gateway.get('/config/cloudsync/mode') == Mode.Enabled

    def suspend(self, wait=True):
        """
        Suspend Cloud Sync

        :param bool wait: Wait for synchronization to stop
        """
        logging.getLogger().info("Suspending cloud sync.")
        self._gateway.put('/config/cloudsync/mode', Mode.Disabled)
        if wait:
            self._track_status(
                [
                    SyncStatus.Off
                ],
                [
                    SyncStatus.Synced,
                    SyncStatus.Syncing,
                    SyncStatus.Scanning,
                    SyncStatus.ConnectingFolders,
                    SyncStatus.InitializingConnection
                ],
                [
                    # No Transient Status
                ],
                [
                    SyncStatus.DisconnectedPortal,
                    SyncStatus.Unlicensed,
                    SyncStatus.ServiceUnavailable,
                    SyncStatus.VolumeUnavailable,
                    SyncStatus.ShouldSupportWinNtAcl,
                    SyncStatus.InternalError,
                    SyncStatus.ClocksOutOfSync,
                    SyncStatus.NoFolder
                ]
            )
        logging.getLogger().info("Cloud sync suspended.")

    def unsuspend(self):
        """ Unsuspend Cloud Sync """
        logging.getLogger().info("Unsuspending cloud sync.")
        self._gateway.put('/config/cloudsync/mode', Mode.Enabled)
        try:
            self._track_status(
                [
                    SyncStatus.Synced,
                    SyncStatus.Syncing,
                    SyncStatus.Scanning
                ],
                [
                    SyncStatus.ConnectingFolders,
                    SyncStatus.InitializingConnection
                ],
                [
                    SyncStatus.DisconnectedPortal,
                    SyncStatus.Unlicensed,
                    SyncStatus.Off
                ],
                [
                    SyncStatus.ServiceUnavailable,
                    SyncStatus.VolumeUnavailable,
                    SyncStatus.ShouldSupportWinNtAcl,
                    SyncStatus.InternalError,
                    SyncStatus.ClocksOutOfSync,
                    SyncStatus.NoFolder
                ]
            )
            logging.getLogger().info('Unsuspended cloud sync.')
        except ErrorStatus as error:
            if error.status == SyncStatus.ShouldSupportWinNtAcl:
                logging.getLogger().warning('Windows ACL enabled folder cannot be synchronized to this device.')
                self._gateway.put('/config/fileservices/share/cloud/access', Acl.WindowsNT)
                logging.getLogger().info('Updated network share access. %s', {'share': 'cloud', 'access': Acl.WindowsNT})
            else:
                logging.getLogger().error("An error occurred while unsuspendeding sync. %s", {'status': error.status})

    def _track_status(self, success, progress, transient, failure):
        track(self._gateway, '/proc/cloudsync/serviceStatus/id', success, progress, transient, failure)

    def refresh(self):
        """ Refresh Cloud Folders """
        logging.getLogger().info("Refreshing cloud folders.")
        self._gateway.execute("/config/cloudsync/cloudExtender", "refreshPaths", None)
        logging.getLogger().info("Completed refreshing cloud folders.")

    def exclude_files(self, extensions=None, filenames=None, paths=None, custom_exclusion_rules=None):
        """
        Exclude files from Cloud Sync. This method will override any existing file exclusion rules
        Use :func:`cterasdk.edge.types.FileExclusionBuilder` to build custom file exclusion rules`

        :param list[str] extensions: List of file extensions
        :param list[str] filenames: List of file names
        :param list[str] paths: List of file paths
        :param list[cterasdk.common.types.FilterBackupSet] rules: Set of custom exclusion rules
        """
        rules = list()
        if extensions:
            param = FilterBackupSet('List of file extensions to exclude from sync',
                                    filter_rules=[FileExclusionBuilder.extensions().include(extensions).build()])
            rules.append(param)
        if filenames:
            param = FilterBackupSet('List of file names to exclude from sync',
                                    filter_rules=[FileExclusionBuilder.names().include(filenames).build()])
            rules.append(param)
        if paths:
            param = FilterBackupSet('List of file paths to exclude from sync',
                                    filter_rules=[FileExclusionBuilder.paths().include(filenames).build()])
            rules.append(param)
        if custom_exclusion_rules:
            rules.extend(custom_exclusion_rules)

        if rules:
            logging.getLogger().info('Setting sync exclusion rules')
            self._gateway.put('/config/cloudsync/excludeFiles', rules)
            logging.getLogger().info('Sync exclusion rules set')

    def remove_file_exclusion_rules(self):
        """
        Remove previously configured sync exclusion rules
        """
        logging.getLogger().info('Removing sync exclusion rules')
        self._gateway.put('/config/cloudsync/excludeFiles', None)
        logging.getLogger().info('Sync exclusion rules removed')


class CloudSyncBandwidthThrottling(BaseCommand):
    """ Edge Filer Cloud Sync Bandwidth Throttling APIs """

    def get_policy(self):
        """
        Get the bandwidth throttling policy

        :returns: a list of bandwidth throttling rules
        :rtype: list[cterasdk.common.types.ThrottlingRule]
        """
        rules = self._gateway.get('/config/cloudsync/syncThrottlingTopic/multiThrottling')
        return [ThrottlingRule.from_server_object(rule) for rule in rules]

    def set_policy(self, rules):
        """
        Set the bandwidth throttling policy

        :param list[cterasdk.common.types.ThrottlingRule] rules: List of bandwidth throttling rules
        """
        return self._gateway.put('/config/cloudsync/syncThrottlingTopic/multiThrottling', [rule.to_server_object() for rule in rules])
