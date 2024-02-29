#!/usr/bin/python3
from cterasdk import ServicesPortal, CTERAException
import cterasdk.settings

from sample_base import CTERASDKSampleBase


class ServicesPortalCreateDirectoriesSample(CTERASDKSampleBase):
    _portal_address_request_string = "the Portal Address"
    _portal_username_request_string = "the user name"
    _directory_name_request_string = "the directory name"

    def __init__(self):
        self._services_portal = None

    def run(self):
        cterasdk.settings.sessions.management.ssl = False
        self._connect_to_portal()

        self._create_directories()

        self._services_portal.logout()

    def _connect_to_portal(self):
        gateway_address = CTERASDKSampleBase._get_input(ServicesPortalCreateDirectoriesSample._portal_address_request_string)
        self._services_portal = ServicesPortal(gateway_address)
        username = CTERASDKSampleBase._get_input(ServicesPortalCreateDirectoriesSample._portal_username_request_string)
        password = CTERASDKSampleBase._get_password(username)
        self._services_portal.login(username, password)

    def _create_directories(self):
        directory_name = CTERASDKSampleBase._get_input(ServicesPortalCreateDirectoriesSample._directory_name_request_string)
        self._services_portal.files.mkdir(directory_name, recurse=True)


if __name__ == "__main__":
    try:
        ServicesPortalCreateDirectoriesSample().run()
    except CTERAException as error:
        print(error)
