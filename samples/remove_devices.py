import logging
import csv

from cterasdk import CTERAException, GlobalAdmin
import cterasdk.settings

from sample_base import CTERASDKSampleBase


class PortalRemoveDevicesSample(CTERASDKSampleBase):
    _portal_address_request_string = "the Portal Address"
    _portal_username_request_string = "the user name"

    def __init__(self):
        self._global_admin = None

    def run(self):
        cterasdk.settings.sessions.management.ssl = False
        self._connect_to_portal()

        self._global_admin.portals.browse('acme')

        with open('devices.csv', newline='\n') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                device_name = row[0]
                logging.getLogger().info('Deleting device. %s', {'name' : device_name})
                try:
                    self._global_admin.execute('/devices/' + device_name, 'delete', 'deviceAndFolders')
                    logging.getLogger().info('Device deleted. %s', {'name' : device_name})
                except CTERAException:
                    logging.getLogger().error('Failed deleting device. %s', {'name' : device_name})

        self._global_admin.logout()

    def _connect_to_portal(self):
        gateway_address = PortalRemoveDevicesSample._get_input(PortalRemoveDevicesSample._portal_address_request_string)
        self._global_admin = GlobalAdmin(gateway_address)
        username = PortalRemoveDevicesSample._get_input(PortalRemoveDevicesSample._portal_username_request_string)
        password = PortalRemoveDevicesSample._get_password(username)
        self._global_admin.login(username, password)


if __name__ == "__main__":
    PortalRemoveDevicesSample().run()
