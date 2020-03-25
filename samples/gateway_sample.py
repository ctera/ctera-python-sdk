import logging

from cterasdk import Gateway, gateway_enum, config, CTERAException

from sample_base import CTERASDKSampleBase


class GatewaySample(CTERASDKSampleBase):
    _gateway_address_request_string = "the Gateway Address"
    _gateway_username_request_string = "the user name"
    _gateway_new_hostname_request_string = "a new hostname for the Gateway"
    _gateway_new_location_request_string = "a new location for the Gateway"
    _gateway_portal_address_request_string = "the Portal Address"
    _gateway_volume_name_request_string = "a name for the Gateway volume"
    _share_directory_name_request_string = "a new for the new shared directory"

    def __init__(self):
        self._device = None
        self._volume_name = None

    def run(self):
        print("CTERA SDK - Gateway Demo")
        self._connect_to_gateway()
        self._device.test()
        self._create_first_user()
        self._create_user()
        self._set_host_name()
        self._set_location()
        self._set_dns_server()
        self._configure_volume()
        self._connect_to_portal()
        self._start_cloud_caching()
        self._disable_first_time_wizard()
        self._create_share()
        print("Demo Completed")

    def _connect_to_gateway(self):
        gateway_address = GatewaySample._get_input(GatewaySample._gateway_address_request_string)
        self._device = Gateway(gateway_address)

    def _create_first_user(self):
        print("Creating the Gateway's first user")
        username = GatewaySample._get_input(GatewaySample._gateway_username_request_string)
        password = GatewaySample._get_password(username)
        self._device.users.add_first_user(username, password)
        print("Logged in as {username}".format(username=username))

    def _create_user(self):
        print("Adding a user to the Gateway")
        username = GatewaySample._get_input(GatewaySample._gateway_username_request_string)
        password = GatewaySample._get_password(username)
        self._device.users.add(username, password, full_name=username, email="{username}@example.com".format(username=username))
        print("User {username} was added successfully".format(username=username))

    def _set_host_name(self):
        print("Setting the Gateway's Host Name")
        new_host_name = GatewaySample._get_input(GatewaySample._gateway_new_hostname_request_string)
        self._device.config.set_hostname(new_host_name)
        print("Gateway Host name was set to {new_host_name}".format(new_host_name=new_host_name))

    def _set_location(self):
        print("Setting the Gateway's Location")
        new_location = GatewaySample._get_input(GatewaySample._gateway_new_location_request_string)
        self._device.config.set_location(new_location)
        print("The Gateway's location was set to {new_location}".format(new_location=new_location))

    def _configure_volume(self):
        print("Configuring the Gateway's volume")
        self._volume_name = GatewaySample._get_input(GatewaySample._gateway_volume_name_request_string)
        self._device.volumes.delete_all()
        self._device.drive.format_all()
        self._device.volumes.add(self._volume_name)
        self._device.afp.disable()
        self._device.ftp.disable()
        self._device.rsync.disable()
        print("The volume {volume_name} was added successfully".format(volume_name=self._volume_name))

    def _set_dns_server(self):
        print("Setting the Gateway's DNS Server to 8.8.8.8")
        ipaddr = self._device.get('/status/network/ports/0/ip')
        self._device.network.set_static_ipaddr(ipaddr.address, ipaddr.netmask, ipaddr.gateway, '8.8.8.8')
        print("DNS Server was set to 8.8.8.8")

    def _connect_to_portal(self):
        print("Connecting the Gateway to the Portal")
        address = GatewaySample._get_input(GatewaySample._gateway_portal_address_request_string)
        username = GatewaySample._get_input(GatewaySample._gateway_username_request_string)
        password = GatewaySample._get_password(username)
        self._device.services.connect(address, username, password)
        print("Successfully connected to Portal at {address}".format(address=address))

    def _start_cloud_caching(self):
        print("Starting Cloud Sync")
        self._device.cache.enable()
        self._device.sync.unsuspend()
        self._device.sync.refresh()
        print("Cloud Sync was configured successfully")

    def _disable_first_time_wizard(self):
        print("Disabling the First Time Wizard")
        self._device.put('/config/gui/openFirstTimeWizard', False)

    def _create_share(self):
        print("Creating a new share")
        share_dir_base_path = 'public'
        directory_name = self._get_input(GatewaySample._share_directory_name_request_string)
        directory_path = '/'.join([share_dir_base_path, directory_name])
        self._device.files.mkdir(directory_path, recurse=True)
        self._device.shares.add(
            directory_name,
            '/'.join([self._volume_name, directory_path]),
            acl=[('LG', 'Everyone', 'RW'), ('LG', 'Administrators', 'RO')],
            access=gateway_enum.Acl.OnlyAuthenticatedUsers
        )
        print("New share was created successfully")


if __name__ == "__main__":
    config.Logging.get().setLevel(logging.DEBUG)
    try:
        GatewaySample().run()
    except CTERAException as error:
        print(error)
