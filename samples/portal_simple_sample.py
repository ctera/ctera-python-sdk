from cterasdk import CTERAException, GlobalAdmin, core_enum, edge_enum, edge_types
import cterasdk.settings

from sample_base import CTERASDKSampleBase


class PortalSimpleSample(CTERASDKSampleBase):
    _portal_address_request_string = "the Portal Address"
    _portal_username_request_string = "the user name"
    _portal_device_name_request_string = "the device name"
    _share_directory_name_request_string = "a new for the new shared directory"

    def __init__(self):
        self._global_admin = None

    def run(self):
        self._connect_to_portal()
        self._handle_users()

        print("Printing all devices")
        self._print_devices()

        print("Printing only vGateways")
        self._print_devices(deviceTypes=['vGateway'], include=['deviceReportedStatus'])

        self._remote_device_operations()
        self._print_system_logs()

        self._global_admin.logout()

    def _connect_to_portal(self):
        gateway_address = CTERASDKSampleBase._get_input(PortalSimpleSample._portal_address_request_string)
        cterasdk.settings.sessions.management.ssl = False
        self._global_admin = GlobalAdmin(gateway_address)
        username = CTERASDKSampleBase._get_input(PortalSimpleSample._portal_username_request_string)
        password = CTERASDKSampleBase._get_password(username)
        self._global_admin.login(username, password)

    def _handle_users(self):
        print("Creating a new user")
        self._global_admin.users.add('alice', 'walice@acme.com', 'Alice', 'Wonderland', 'password1!', core_enum.Role.ReadWriteAdmin)
        print("User was created succussfully")

        print("Deleting previously created user")
        self._global_admin.users.delete('alice')
        print("User was deleted successfully")

    def _print_devices(self, deviceTypes=None, include=None):
        for device in self._global_admin.devices.filers(include=include, deviceTypes=deviceTypes):
            print(device)

    def _remote_device_operations(self):
        print("Creating a new share")
        device_name = CTERASDKSampleBase._get_input(PortalSimpleSample._portal_device_name_request_string)
        device = self._global_admin.devices.device(device_name)
        share_dir_base_path = 'public'
        directory_name = self._get_input(PortalSimpleSample._share_directory_name_request_string)
        directory_path = '/'.join([share_dir_base_path, directory_name])
        device.shares.add(
            directory_name,
            '/'.join(['main', directory_path]),
            acl=[
                edge_types.ShareAccessControlEntry(type='LG', name='Everyone', perm='RW'),
                edge_types.ShareAccessControlEntry(type='LG', name='Administrators', perm='RO')
            ],
            access=edge_enum.Acl.OnlyAuthenticatedUsers
        )
        print("New Share was created successfully")
        print("Deleting previosly created share")
        device.shares.delete(directory_name)
        print("Share was deleted successfully")

    def _print_system_logs(self):
        print("Printing Cloud Sync logs")
        for log in self._global_admin.logs.logs(topic=core_enum.LogTopic.CloudSync):
            print(log.msg)


if __name__ == "__main__":
    try:
        PortalSimpleSample().run()
    except CTERAException as error:

        print(error)
