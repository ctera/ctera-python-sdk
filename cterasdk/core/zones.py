import copy
import logging
import re

from .base_command import BaseCommand
from . import query
from . import devices
from . import cloudfs
from . import enum
from ..common import Object
from ..exception import CTERAException


class Zones(BaseCommand):
    """
    Portal Zones APIs
    """

    def get(self, name):
        """
        Get zone by name

        :param str name: The name of the zone to get
        :return: The requested zone
        """
        query_filter = query.FilterBuilder('name').eq(name)
        param = query.QueryParamBuilder().include_classname().startFrom(0).countLimit(1).addFilter(query_filter).orFilter(False).build()

        logging.getLogger().info('Retrieving zone. %s', {'name': name})

        response = self._portal.execute('', 'getZonesDisplayInfo', param)

        objects = response.objects
        if len(objects) < 1:
            logging.getLogger().error('Zone not found. %s', {'name': name})
            raise CTERAException('Zone not found', None, name=name)

        zone = objects[0]
        logging.getLogger().info('Zone found. %s', {'name': name, 'id': zone.zoneId})
        return zone

    def add(self, name, policy_type=enum.PolicyType.SELECT, description=None):
        """
        Add a new zone

        :param str name: The name of the new zone
        :param cterasdk.core.enum.PolicyType,optional policy_type:
         Policy type of the new zone, defaults to cterasdk.core.enum.PolicyType.SELECT
        :param str,optional description: The description of the new zone
        """
        param = self._zone_param(name, policy_type, description)

        logging.getLogger().info('Adding zone. %s', {'name': name})

        response = self._portal.execute('', 'addZone', param)
        try:
            self._process_response(response)
        except CTERAException as error:
            logging.getLogger().error('Zone creation failed. %s', {'rc': response.rc})
            raise error
        logging.getLogger().info('Zone added. %s', {'name': name})

    def delete(self, name):
        """
        Delete a zone

        :param str name: The name of the zone to delete
        """
        zone = self._portal.zones.get(name)
        logging.getLogger().info('Deleting zone. %s', {'zone': name})
        response = self._portal.execute('', 'deleteZones', [zone.zoneId])
        if response == 'ok':
            logging.getLogger().info('Zone deleted. %s', {'zone': name})

    def add_devices(self, name, device_names):
        """
        Add devices to a zone

        :param str name: The name of the zone to add devices to
        :param list[str] device_names: The names of the devices to add to the zone
        """
        zone = self._portal.zones.get(name)
        portal_devices = devices.Devices(self._portal).by_name(include=['uid'], names=device_names)
        info = self._zone_info(zone.zoneId)
        description = (info.description if hasattr(info, 'description') else None)

        param = self._zone_param(info.name, info.policyType, description, info.zoneId)
        for portal_device in portal_devices:
            param.delta.devicesDelta.added.append(portal_device.uid)

        logging.getLogger().info('Adding devices to zone. %s', {'zone': info.name})

        try:
            self._save(param)
        except CTERAException as error:
            logging.getLogger().error('Failed adding devices to zone.')
            raise CTERAException('Failed adding devices to zone', error, zone=name, devices=device_names)

    def add_folders(self, name, folder_finding_helpers):
        """
        Add the folders to the zone

        :param str name: The name of the zone
        :param list[cterasdk.core.types.CloudFSFolderFindingHelper] folder_finding_helpers: List of folder names and owners
        """
        zone = self._portal.zones.get(name)
        folders = self._find_folders(folder_finding_helpers)
        info = self._zone_info(zone.zoneId)
        description = info.description if hasattr(info, 'description') else None
        param = self._zone_param(info.name, info.policyType, description, info.zoneId)
        param.delta.policyDelta = []

        for owner_id, folder_ids in folders.items():
            policyDelta = Object()
            policyDelta._classname = 'ZonePolicyDelta'  # pylint: disable=protected-access
            policyDelta.userUid = owner_id
            policyDelta.foldersDelta = Object()
            policyDelta.foldersDelta._classname = 'ZoneFolderDelta'  # pylint: disable=protected-access
            policyDelta.foldersDelta.added = copy.deepcopy(folder_ids)
            policyDelta.foldersDelta.removed = []

            param.delta.policyDelta.append(policyDelta)

        try:
            self._save(param)
        except CTERAException as error:
            logging.getLogger().error('Failed adding folders to zone.')
            raise CTERAException('Failed adding folders to zone', error, zone=name)

    def _zone_info(self, zid):
        logging.getLogger().debug('Obtaining zone info. %s', {'id': zid})
        response = self._portal.execute('', 'getZoneBasicInfo', zid)
        logging.getLogger().debug('Obtained zone info. %s', {'id': zid})
        return response

    def _find_folders(self, folder_finding_helpers):
        folders = {}
        for folder_finding_helper in folder_finding_helpers:
            cloud_folder = cloudfs.CloudFS(self._portal).find(
                folder_finding_helper.name,
                folder_finding_helper.owner,
                include=['uid', 'owner']
            )
            folder_id = cloud_folder.uid
            owner_id = re.search("[1-9][0-9]*", cloud_folder.owner).group(0)

            if folders.get(owner_id) is None:
                folders[owner_id] = [folder_id]
            else:
                folders.get(owner_id).append(folder_id)

        return folders

    def _save(self, param):
        zone_name = param.basicInfo.name

        logging.getLogger().debug('Applying changes to zone. %s', {'zone': param.basicInfo.name})

        response = self._portal.execute('', 'saveZone', param)
        try:
            self._process_response(response)
        except CTERAException as error:
            logging.getLogger().error('Failed applying changes to zone. %s', {'zone': zone_name, 'rc': response.rc})
            raise error

        logging.getLogger().debug('Zone changes applied successfully. %s', {'zone': zone_name})

    @staticmethod
    def _process_response(response):
        if response.rc != 'OK':
            raise CTERAException('Zone creation failed', response)

    @staticmethod
    def _zone_param(name, policy_type, description=None, zid=None):
        param = Object()
        param._classname = "SaveZoneParam"  # pylint: disable=protected-access
        param.basicInfo = Object()
        param.basicInfo._classname = 'ZoneBasicInfo'  # pylint: disable=protected-access
        param.basicInfo.name = name
        param.basicInfo.policyType = policy_type
        param.basicInfo.description = description
        param.basicInfo.zoneId = zid
        param.delta = Object()
        param.delta._classname = 'ZoneDelta'  # pylint: disable=protected-access
        param.delta.devicesDelta = Object()
        param.delta.devicesDelta._classname = 'ZoneDeviceDelta'  # pylint: disable=protected-access
        param.delta.devicesDelta.added = []
        param.delta.devicesDelta.removed = []

        return param
