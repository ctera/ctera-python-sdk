import logging

from ..lib import track, ErrorStatus
from .enum import Mode, SyncStatus, Acl
from .base_command import BaseCommand
from ..common import ThrottlingRule


class Sync(BaseCommand):
    """ Gateway Cloud Sync APIs """

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

    def suspend(self):
        """ Suspend Cloud Sync """
        logging.getLogger().info("Suspending cloud sync.")
        self._gateway.put('/config/cloudsync/mode', Mode.Disabled)
        logging.getLogger().info("Cloud sync suspended.")

    def unsuspend(self):
        """ Unsuspend Cloud Sync """
        logging.getLogger().info("Unsuspending cloud sync.")
        self._gateway.put('/config/cloudsync/mode', Mode.Enabled)
        try:
            ref = '/proc/cloudsync/serviceStatus/id'
            track(
                self._gateway,
                ref,
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

    def refresh(self):
        """ Refresh Cloud Folders """
        logging.getLogger().info("Refreshing cloud folders.")
        self._gateway.execute("/config/cloudsync/cloudExtender", "refreshPaths", None)
        logging.getLogger().info("Completed refreshing cloud folders.")


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
