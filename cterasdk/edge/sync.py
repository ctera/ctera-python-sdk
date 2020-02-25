import logging

from ..lib import track, ErrorStatus
from .enum import Mode, SyncStatus, Acl
from .base_command import BaseCommand


class Sync(BaseCommand):

    def suspend(self):
        logging.getLogger().info("Suspending cloud sync.")
        self._gateway.put('/config/cloudsync/mode', Mode.Disabled)
        logging.getLogger().info("Cloud sync suspended.")

    def unsuspend(self):
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
        logging.getLogger().info("Refreshing cloud folders.")
        self._gateway.execute("/config/cloudsync/cloudExtender", "refreshPaths", None)
        logging.getLogger().info("Completed refreshing cloud folders.")
