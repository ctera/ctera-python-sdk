# pylint: disable=too-many-lines
import argparse
import asyncio
import logging
import sys
from datetime import datetime

from .. import settings
from ..objects.asynchronous.core import AsyncGlobalAdmin
from ..common import Object, parse_base_object_ref
from ..convert.deserializers import fromjsonstr
from ..exceptions.auth import AuthenticationError
from ..exceptions.transport import HTTPError


logger = logging.getLogger('cterasdk.export')


ATTRIBUTE_PATHS = {

    '.': [
        'insight.globalStatus.status',
        'insight.settings.enabled',
        'mcp.globalStatus.status',
        'mediaConnector.globalStatus.status',
        'mediaConnector.settings.enabled',
        'messaging.globalStatus.status',
        'syslog.status.globalStatus.status',
        'varonis.globalStatus.status',
        'samlCertificate'
    ],

    '.settings.': [
        'ca.expirationDate',
        'cloudFSSettings.loadBlocksMaxThreads',
        'cloudFSSettings.mapFileInDB',
        'cloudFSSettings.maxThreadsForMigration',
        'cloudFSSettings.storeBlocksMaxThreads',
        'cteraZonesEnabled',
        'cteraZonesTaskMode',
        'cteraZonesTaskRecalcIntervalInSeconds',
        'dnsSuffix',
        'officeOnlineSettings.enabled'
    ],

    '.portalLicenses[].': [
        'antivirus',
        'appliances',
        'archiveStorage',
        'cloudDrives',
        'cloudDrivesLite',
        'comment',
        'dlp',
        'expirationDate',
        'expired',
        'globalFileLock',
        'key',
        'keyManager',
        'originalKey',
        'portalLicense',
        'serverAgents',
        'storage',
        'vGateways128',
        'vGateways256',
        'vGateways32',
        'vGateways4',
        'vGateways64',
        'vGateways8',
        'valid',
        'varonis',
        'workstationAgents',
    ],

    '.firmwares[].': [
        'binaryDataMD5',
        'firmwareType',
        'guid',
        'isDefault',
        'uid',
        'version',
    ],

    '.servers[].': [
        'backupToBucket.details.endPoint',
        'backupToBucket.details.storage',
        'backupToBucket.details.trustAllCertificates',
        'backupToBucket.details.useHttps',
        'backupToBucket.details.usePathStyleAddressing',
        'backupToBucket.enabled',
        'backupToBucket.exportSchedulePeriod',
        'backupToBucket.status',
        'connected',
        'createDate',
        'isAVBGServer',
        'isApplicationServer',
        'isMessagingServer',
        'isS3Endpoint',
        'isThumbnailsServer',
        'mainDB',
        'modifiedDate',
        'name',
        'previewStatus',
        'renderingServer',
        'replicationSettings.replicationOf',
        'runningVersion',
        'systemInfo',
    ],

    '.locations[].': [
        'bucket',
        'connected',
        'createDate',
        'dedicated',
        'dedicatedPortal',
        'directUpload',
        'doFsync',
        'endPoint',
        'folderSize',
        'httpsOnly',
        'modifiedDate',
        'name',
        'objectLock',
        'readOnly',
        's3Endpoint',
        'status',
        'storage',
        'storageClass',
        'trustAllCertificates',
        'useHttps',
        'usePathStyleAddressing',
    ],

    '.portals[].': [
        'activationStatus',
        'externalPortalId',
        'isDefault',
        'name',
        'numberOfAddons',
        'numberOfConnectedDevices',
        'numberOfUsers',
        'plan.archiveStorage.amount',
        'plan.cloudDrives.amount',
        'plan.cloudDrivesLite.amount',
        'plan.retentionPolicy',
        'plan.serverAgents.amount',
        'plan.services[].serviceName',
        'plan.services[].serviceState',
        'plan.storage.amount',
        'plan.vGateways.amount',
        'plan.vGateways128.amount',
        'plan.vGateways256.amount',
        'plan.vGateways32.amount',
        'plan.vGateways4.amount',
        'plan.vGateways64.amount',
        'plan.vGateways8.amount',
        'plan.workstationAgents.amount',
        'portalTrashcanInfo.isTrashcan',
        'portalType',
        'resourcesQuotas[].resourceType',
        'resourcesQuotas[].totalQuota',
        'resourcesQuotas[].usedQuota',
        'totalArchiveStorageQuota',
        'totalStorageQuota',
        'uid',
        'usedArchiveStorageQuota',
        'usedStorageQuota',
    ],

    '.portals[].foldersGroups[].': [
        'averageBlockSizeKb',
        'averageMapFileSizeKb',
        'compressionMethod',
        'createDate',
        'deduplicationMethodType',
        'encryptionMode',
        'fixedBlockSizeKb',
        'mapFileInDB',
        'modifiedDate',
        'name',
        'storageClass',
        'uid',
    ],

    '.portals[].cloudDrives[].': [
        'archiveSettings.archive',
        'archiveSettings.deleteData',
        'archiveSettings.gracePeriod.amount',
        'archiveSettings.gracePeriod.type',
        'archiveSettings.retentionMode',
        'archiveSettings.retentionPeriod.amount',
        'archiveSettings.retentionPeriod.type',
        'archiveSettings.seal',
        'createDate',
        'enableSyncWinNtExtendedAttributes',
        'extendedAttributes.enable',
        'folderQuota',
        'folderStats.cloudFolderSize',
        'folderStats.cloudFolderSize.totalFiles',
        'globalFileLockSettings.enabled',
        'globalFileLockSettings.globalFileLockExtensions',
        'group',
        'isDeleted',
        'modifiedDate',
        'owner',
        'teamProject',
        'uid',
        'wormSettings.gracePeriod.amount',
        'wormSettings.gracePeriod.type',
        'wormSettings.retentionMode',
        'wormSettings.retentionPeriod.amount',
        'wormSettings.retentionPeriod.type',
        'wormSettings.worm',
    ],

    '.portals[].zones[].': [
        'cloudfolders[].isIncluded',
        'cloudfolders[].owner.uid',
        'cloudfolders[].totalFiles',
        'cloudfolders[].totalSize',
        'cloudfolders[].uid',
        'devices[].deviceType',
        'devices[].uid',
        'devicesCount',
        'isDefault',
        'name',
        'policyType',
        'zoneId',
        'zoneStatistics.totalFiles',
        'zoneStatistics.totalFolders',
        'zoneStatistics.totalSize',
    ],

    '.portals[].devices[].': [
        'backup.backupStatus.backupHistory.lastSuccessfulSync',
        'backup.backupStatus.backupHistory.totalFiles',
        'backup.backupStatus.backupHistory.totalSize',
        'backup.backupStatus.deviceTime.LocalTime',
        'backup.backupStatus.deviceTime.TimeGMT',
        'backup.backupStatus.deviceTime.uptime',
        'backup.backupStatus.serviceStatus.desc',
        'config.device.location',
        'config.services.remoteAccess.adminRemoteAccess',
        'createDate',
        'deviceConnectionStatus.connected',
        'deviceConnectionStatus.updateTime',
        'deviceReportedStatus.status.device.deviceReportedStatus',
        'deviceReportedStatus.status.device.installedFirmware.md5',
        'deviceReportedStatus.status.device.installedFirmware.version',
        'deviceReportedStatus.status.device.platform',
        'deviceReportedStatus.status.device.portalFirmware.guid',
        'deviceReportedStatus.status.device.portalFirmware.md5',
        'deviceReportedStatus.status.device.SerialNumber',
        'deviceType',
        'metadata.config.av.realtime.mode',
        'metadata.cloudsync.cloudExtender.operationMode',
        'metadata.cloudsync.cloudExtender.selectedFolders',
        'metadata.config.fileservices.cifs.SMBEncryption',
        'metadata.config.fileservices.cifs.mode',
        'metadata.config.fileservices.cifs.packetSigning',
        'metadata.config.fileservices.cifs.passwordServer',
        'metadata.config.fileservices.cifs.type',
        'metadata.config.fileservices.ftp.RequireSSL',
        'metadata.config.fileservices.ftp.mode',
        'metadata.config.fileservices.nfs.aggregateWrites',
        'metadata.config.fileservices.nfs.async',
        'metadata.config.fileservices.nfs.krb5',
        'metadata.config.fileservices.nfs.mode',
        'metadata.config.fileservices.nfs.nfsv4enabled',
        'metadata.config.fileservices.share[].access',
        'metadata.config.fileservices.share[].acl',
        'metadata.config.fileservices.share[].clientSideCaching',
        'metadata.config.fileservices.share[].exportToFTP',
        'metadata.config.fileservices.share[].exportToNFS',
        'metadata.config.fileservices.share[].exportToWebdav',
        'metadata.config.fileservices.share[].screenedFileTypesEnabled',
        'metadata.config.fileservices.share[].trustedNFSClients',
        'metadata.config.dedup.useLocalMapFileDedup',
        'metadata.config.ransomProtect.enableHoneypot',
        'metadata.config.ransomProtect.enabled',
        'metadata.config.snmp.mode',
        'metadata.config.snmp.snmpV3.mode',
        'metadata.status.storage.arrays[].activeDevices',
        'metadata.status.storage.arrays[].allocatedCapacity',
        'metadata.status.storage.arrays[].availableCapacity',
        'metadata.status.storage.arrays[].failedDevices',
        'metadata.status.storage.arrays[].logicalCapacity',
        'metadata.status.storage.arrays[].name',
        'metadata.status.storage.arrays[].spareDevices',
        'metadata.status.storage.arrays[].state',
        'metadata.status.storage.arrays[].workingDevices',
        'metadata.status.storage.disks[].allocatedCapacity',
        'metadata.status.storage.disks[].availableCapacity',
        'metadata.status.storage.disks[].bus',
        'metadata.status.storage.disks[].capacity',
        'metadata.status.storage.disks[].logicalCapacity',
        'metadata.status.storage.disks[].name',
        'metadata.status.storage.disks[].status',
        'metadata.status.storage.summary.allocatedDriveSpace',
        'metadata.status.storage.summary.availableDriveSpace',
        'metadata.status.storage.summary.encryptedVolumeCount',
        'metadata.status.storage.summary.logicalDriveSpace',
        'metadata.status.storage.summary.physicalDriveSpace',
        'metadata.status.storage.summary.spareDriveCount',
        'metadata.status.storage.summary.state',
        'metadata.status.storage.summary.totalDriveCount',
        'metadata.status.storage.summary.totalVolumeCount',
        'metadata.status.storage.summary.unusedDriveCount',
        'metadata.status.storage.volumes[].fileSystemType',
        'metadata.status.storage.volumes[].name',
        'metadata.status.storage.volumes[].status',
        'modifiedDate',
        'owner',
        'proc.storage.summary.freeVolumeSpace',
        'proc.storage.summary.totalVolumeSpace',
        'proc.storage.summary.usedVolumeSpace',
        'storage.status.summary.allocatedDriveSpace',
        'storage.status.summary.availableDriveSpace',
        'storage.status.summary.encryptedVolumeCount',
        'storage.status.summary.logicalDriveSpace',
        'storage.status.summary.physicalDriveSpace',
        'storage.status.summary.spareDriveCount',
        'storage.status.summary.state',
        'storage.status.summary.totalDriveCount',
        'storage.status.summary.totalVolumeCount',
        'storage.status.summary.unusedDriveCount',
        'uid',
        'version',
    ],
}


ANONYMIZE_ATTRIBUTES = [
    '.portals[].cloudDrives[].owner',
    '.portals[].cloudDrives[].group',
    '.portals[].devices[].owner',
    '.locations[].storageClass',
    '.locations[].dedicatedPortal',
    '.portals[].foldersGroups[].storageClass'
]


COUNT_ATTRIBUTES = [
    '.portals[].devices[].metadata.config.fileservices.share[].acl',
    '.portals[].devices[].metadata.config.fileservices.share[].trustedNFSClients'
]


def filter_object(o, attribute_paths):
    tree = {}

    for prefix, attributes in attribute_paths.items():
        for attribute in attributes:
            current = tree
            for part in f'{prefix}{attribute}'.lstrip('.').split('.'):
                is_list = part.endswith('[]')
                name = part.removesuffix('[]')
                current = current.setdefault(name, (is_list, {}))[1]

    return _filter_object(o, tree)


def _filter_object(o, tree):
    result = Object()

    for name, (is_list, children) in tree.items():
        if not hasattr(o, name):
            continue

        value = getattr(o, name)

        if value is None or not children:
            setattr(result, name, value)
        elif is_list:
            setattr(result, name, [
                _filter_object(item, children) if item is not None else None
                for item in value
            ])
        else:
            setattr(result, name, _filter_object(value, children))

    return result if vars(result) else None


def transform_attributes(o, attributes, transform):
    for attribute in attributes:
        _transform_attribute(o, attribute.lstrip('.').split('.'), transform)
    return o


def _transform_attribute(o, parts, transform):
    if o is None:
        return

    part = parts[0]

    if part.endswith('[]'):
        for item in getattr(o, part[:-2], None) or []:
            _transform_attribute(item, parts[1:], transform)
        return

    value = getattr(o, part, None)

    if value is None:
        return

    if len(parts) == 1:
        setattr(o, part, transform(value))
    else:
        _transform_attribute(value, parts[1:], transform)


def anonymize_uids(o, attributes):
    return transform_attributes(
        o,
        attributes,
        lambda value: int(parse_base_object_ref(value).uid),
    )


def count_attributes(o, attributes):
    return transform_attributes(
        o,
        attributes,
        len,
    )


def expand_portal_schema(array, portals, attribute, identifier='portal'):
    for element in array:
        value = getattr(element, identifier)
        if value:
            portal = portals[int(parse_base_object_ref(value).uid)]
            getattr(portal, attribute).append(element)


async def enumerate_devices(admin, inspect=True, max_workers=5):
    """
    Enumerate devices, including general metadata captured by CTERA Portal.

    Args:
        admin: Global administrator session.
        inspect (bool, optional): Inspect the configuration of connected devices. Defaults to True.
        max_workers (int, optional): Max number of concurrent requests for inspection. Defaults to 5.

    Returns:
        dict: A dictionary mapping an Edge Filer's unique numeric ID to either its
        raw device object (if inspect=False) or its configuration object (if inspect=True).
    """
    devices = [device async for device in admin.devices.devices([
        'uid',
        'name',
        'portal',
        'version',
        'owner',
        'createDate',
        'modifiedDate',
        'deviceType',
        'deviceConnectionStatus',
        'deviceReportedStatus'
    ], allPortals=True)]

    def serialize(device):
        return fromjsonstr(str(device))

    devices = await inspect_devices(devices, max_workers) if inspect else devices

    return [serialize(device) for device in devices]


async def inspect_devices(devices, max_workers):
    """
    Inspect the configuration of connected devices.

    Args:
        devices (dict): A dictionary mapping device UIDs to device objects.
        max_workers (int): Max number of concurrent requests.

    Returns:
        dict: A dictionary mapping an Edge Filer's unique numeric ID to its configuration object.
    """

    def inspectable(device):
        return (
            device.deviceType in ['vGateway', 'C200', 'C400', 'C800', 'C800P', 'VBox', 'CloudPlug']
            and device.deviceConnectionStatus.connected
        )

    async def inspect_device(device, semaphore):
        async with semaphore:
            try:
                device.metadata = await device.api.get_multi('/', [
                    '/config/fileservices/nfs',
                    '/config/fileservices/ftp',
                    '/config/fileservices/cifs',
                    '/config/fileservices/share',
                    '/config/av/realtime',
                    '/config/ransomProtect',
                    '/config/snmp',
                    '/config/dedup/useLocalMapFileDedup',
                    '/status/storage',
                    '/config/cloudsync/cloudExtender/selectedFolders',
                    '/config/cloudsync/metadataPinning',
                    '/config/cloudsync/cloudExtender/operationMode'
                ])
            except HTTPError:
                logger.error("Could not inspect device metadata for device (name=%s, uid=%s).", device.name, device.uid)
            return device

    tasks = []
    semaphore = asyncio.Semaphore(max_workers)

    for device in devices:
        if inspectable(device):
            tasks.append(inspect_device(device, semaphore))

    return await asyncio.gather(*tasks)


async def enumerate_portals(admin):
    """
    Enumerate Virtual Portals.

    Args:
        admin: Global administrator session.

    Returns:
        dict: A dictionary mapping an Virtual Portal's unique numeric ID to Virtual Portal objects.
    """
    return {portal.uid: portal async for portal in admin.portals.tenants()}


async def enumerate_cloudfolders(admin, portals):
    """
    Enumerate Cloud Drive Folders.

    Args:
        admin: Global administrator session.
        portals (list(str)): A list of Virtual Portal names.
    """
    include = [
        "uid",
        "createDate",
        "modifiedDate",
        "enableSyncWinNtExtendedAttributes",
        "extendedAttributes.enable",
        "folderStats.cloudFolderSize",
        "folderStats.totalFiles",
        "globalFileLockSettings",
        "group",
        "owner",
        "portal",
        "teamProject",
        "folderQuota",
        "isDeleted",
        "wormSettings",
        "archiveSettings",
        "openFabricSettings.storageMode",
        "openFabricSettings.dataStorage.storage",
        "openFabricStorageStatus",
        "openStorageEnabled"
    ]

    return [drive async for drive in admin.cloudfs.drives.all(include, portals)]


async def enumerate_zones(admin, portals):
    """
    Enumerate Zones.

    Args:
        admin: Global administrator session.
        portals (list(str)): A list of Virtual Portal names.
    """
    return {portal: [zone async for zone in admin.cloudfs.zones.all(True, [portal])] for portal in portals}


async def enumerate_folder_groups(admin, portals):
    """
    Enumerate Folder Groups.

    Args:
        admin: Global administrator session.
        portals (list(str)): A list of Virtual Portal names.
    """
    include = [
        "uid",
        "portal",
        "createDate",
        "modifiedDate",
        "deduplicationMethodType",
        "fixedBlockSizeKb",
        "averageBlockSizeKb",
        "averageMapFileSizeKb",
        "mapFileInDB",
        "storageClass",
        "encryptionMode",
        "compressionMethod",
    ]

    return [group async for group in admin.cloudfs.groups.all(include, portals)]


async def enumerate_exports(admin, portals):
    """
    Enumerate Fusion Direct S3 Exports.

    Args:
        admin: Global administrator session.
        portals (list(str)): A list of Virtual Portal names.
    """
    return [export async for export in admin.cloudfs.exports.all(portals)]


async def enumerate_subscription_plans(admin):
    """
    Expand subscription plans.

    Args:
        admin: Global administrator session.
    """
    include = [
        'uid',
        'services',
        'archiveStorage',
        'vGateways',
        'vGateways4',
        'vGateways8',
        'vGateways32',
        'vGateways64',
        'vGateways128',
        'vGateways256',
        'storage',
        'cloudDrives',
        'cloudDrivesLite',
        'serverAgents',
        'workstationAgents',
        'createDate',
        'modifiedDate',
        'retentionPolicy'
    ]
    return {plan.uid: plan async for plan in admin.plans.list_plans(include)}


async def enumerate_servers(admin):
    """
    Enumerate servers.

    Args:
        admin: Global administrator session.
    """
    include = [
        'createDate',
        'modifiedDate',
        'connected',
        'name',
        'mainDB',
        'isAVBGServer',
        'isApplicationServer',
        'isMessagingServer',
        'isS3Endpoint',
        'isThumbnailsServer',
        'renderingServer',
        'previewStatus',
        'runningVersion',
        'replicationSettings.replicationOf',
        'systemInfo',
        'backupToBucket'
    ]
    return [server async for server in admin.servers.list_servers(include)]


async def enumerate_locations(admin):
    """
    Enumerate Storage Nodes.

    Args:
        admin: Global administrator session.
    """
    include = [
        "connected",
        "name",
        "storage",
        "bucket",
        "readOnly",
        "status",
        "dedicated",
        "dedicatedPortal",
        "directUpload",
        "httpsOnly",
        "useHttps",
        "trustAllCertificates",
        "objectLock",
        "usePathStyleAddressing",
        "s3Endpoint",
        "endPoint",
        "createDate",
        "modifiedDate",
        "storageClass",
        "doFsync",
        "folderSize"
    ]

    return [node async for node in admin.buckets.list_buckets(include)]


async def inspect_environment(admin):
    """
    Enumerate global licenses, firmwares, settings and microservices.

    Args:
        admin: Global administrator session.
    """
    root = await admin.v1.api.get_multi('', [
        '/portalLicenses',
        '/firmwares',
        '/settings'
    ])
    root.microservices = await admin.v1.api.get('/microservices')
    return root


async def export_objects(admin):
    """
    Enumerate every object CTERA Portal exposes, chain it into a single object, then
    filter it down to the attributes in ATTRIBUTE_PATHS and anonymize/count as configured.

    Args:
        admin: Global administrator session.
    """

    logger.info('Retrieving global settings, portals, servers and storage nodes...')
    root, portals, servers, locations = await asyncio.gather(
        inspect_environment(admin),
        enumerate_portals(admin),
        enumerate_servers(admin),
        enumerate_locations(admin)
    )

    names = [portal.name for portal in portals.values()]

    logger.info('Retrieving plans, folder groups, cloud drives, zones, exports and devices '
                '(device inspection may take a few minutes)...')
    plans, folder_groups, cloudfolders, zones, buckets, devices = await asyncio.gather(
        enumerate_subscription_plans(admin),
        enumerate_folder_groups(admin, names),
        enumerate_cloudfolders(admin, names),
        enumerate_zones(admin, names),
        enumerate_exports(admin, names),
        enumerate_devices(admin, True)
    )

    for portal in portals.values():
        portal.plan = plans[int(parse_base_object_ref(portal.plan).uid)]
        portal.locations = []
        portal.foldersGroups = []
        portal.cloudDrives = []
        portal.zones = zones[portal.name]
        portal.buckets = []
        portal.devices = []

    expand_portal_schema(locations, portals, 'locations', 'dedicatedPortal')
    expand_portal_schema(folder_groups, portals, 'foldersGroups')
    expand_portal_schema(cloudfolders, portals, 'cloudDrives')
    expand_portal_schema(buckets, portals, 'buckets')
    expand_portal_schema(devices, portals, 'devices')

    root.servers = servers
    root.locations = locations
    root.portals = list(portals.values())

    logger.info('Filtering, anonymizing and counting collected data...')
    result = filter_object(root, ATTRIBUTE_PATHS)
    result = anonymize_uids(result, ANONYMIZE_ATTRIBUTES)
    result = count_attributes(result, COUNT_ATTRIBUTES)

    return result


async def main(args):
    async with AsyncGlobalAdmin(args.address) as admin:
        try:
            await admin.login(args.user, args.password)
        except AuthenticationError as error:
            logger.error("Login to %s as '%s' failed: %s", args.address, args.user, error)
            return None

        try:
            return await export_objects(admin)
        except HTTPError as error:
            logger.error('Failed to export objects from %s: %s', args.address, error)
            return None
        finally:
            await admin.logout()


def configure_logging(debug):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(name)s: %(message)s',
    )


def configure_transport_layer_security(no_verify):
    settings.core.asyn.settings.connector.ssl = not no_verify


def parse_args():
    parser = argparse.ArgumentParser(description='CTERA Global File System - Configuration State Snapshot.')
    parser.add_argument('-a', dest='address', required=True, help='CTERA Portal address')
    parser.add_argument('-u', dest='user', required=True, help='Support or read-only admin username')
    parser.add_argument('-p', dest='password', required=True, help='Support or read-only admin password')
    parser.add_argument('-o', '--output', default=None,
                         help='Path to write the export file to (default: <datetime>.<address>.cterasdk.export.json)')
    parser.add_argument('--no-verify', action='store_true', help='Disable TLS verification')
    parser.add_argument('--debug', action='store_true', help='Enable verbose (debug) logging')
    parser.add_argument('--shared', action='store_true', help='Enable if this Portal serves multiple distinct organizations.')
    args = parser.parse_args()

    if not args.output:
        args.output = f'{datetime.now():%Y%m%d_%H%M%S}.{args.address}.cterasdk.export.json'

    return args


def run():
    args = parse_args()
    configure_logging(args.debug)
    configure_transport_layer_security(args.no_verify)

    result = asyncio.run(main(args))
    if result is None:
        sys.exit(1)

    result.site = Object(**{
        'type': 'shared' if args.shared else 'private'
    })

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(str(result))
    logger.info('Export written to %s', args.output)
