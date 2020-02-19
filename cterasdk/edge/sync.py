from ..lib import track, ErrorStatus

from .enum import Mode, SyncStatus, Acl

import logging

def suspend(CTERAHost):
    
    logging.getLogger().info("Suspending cloud sync.")
    
    CTERAHost.put('/config/cloudsync/mode', Mode.Disabled)
    
    logging.getLogger().info("Cloud sync suspended.")
    
def unsuspend(CTERAHost):
    
    logging.getLogger().info("Unsuspending cloud sync.")
    
    CTERAHost.put('/config/cloudsync/mode', Mode.Enabled)
    
    try:
    
        ref = '/proc/cloudsync/serviceStatus/id'
    
        status = track(CTERAHost, ref, [SyncStatus.Synced, SyncStatus.Syncing, SyncStatus.Scanning], [SyncStatus.ConnectingFolders, SyncStatus.InitializingConnection], [SyncStatus.DisconnectedPortal, SyncStatus.Unlicensed, SyncStatus.Off], [SyncStatus.ServiceUnavailable, SyncStatus.VolumeUnavailable, SyncStatus.ShouldSupportWinNtAcl, SyncStatus.InternalError, SyncStatus.ClocksOutOfSync, SyncStatus.NoFolder])
        
        logging.getLogger().info('Unsuspended cloud sync.')

    except ErrorStatus as error:
        
        if error.status == SyncStatus.ShouldSupportWinNtAcl:
            
            logging.getLogger().warn('Windows ACL enabled folder cannot be synchronized to this device.')

            CTERAHost.put('/config/fileservices/share/cloud/access', Acl.WindowsNT)

            logging.getLogger().info('Updated network share access. {0}'.format({'share' : 'cloud', 'access': Acl.WindowsNT }))
            
        else:
            
            logging.getLogger().error("An error occurred while unsuspendeding sync. {0}".format({'status' : error.status}))
    
def refresh(CTERAHost):
    
    logging.getLogger().info("Refreshing cloud folders.")
    
    CTERAHost.execute("/config/cloudsync/cloudExtender", "refreshPaths", None)
    
    logging.getLogger().info("Completed refreshing cloud folders.")