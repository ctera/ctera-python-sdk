from urllib.parse import urlparse
from .enum import DeviceType
from ..objects.synchronous import edge, drive


def _relay_base(Portal, device):
    device_dns = getattr(device, 'deviceDnsName', None)
    if device_dns and device_dns.startswith(f'{device.name}.'):
        portal_hostname = device_dns[len(device.name) + 1:]
        parsed = urlparse(Portal.ctera.baseurl)
        port = f':{parsed.port}' if parsed.port not in (None, 80, 443) else ''
        base_path = parsed.path.rstrip('/')
        return f'{parsed.scheme}://{portal_hostname}{port}{base_path}/devices/{device.name}'
    return f'{Portal.ctera.baseurl.rstrip("/")}/devices/{device.name}'


def remote_command(Portal, device):
    base = _relay_base(Portal, device)

    ManagedDevice = None
    if device.deviceType in DeviceType.Gateways:
        ManagedDevice = edge.Edge(Portal=Portal, base=base)
    elif device.deviceType in DeviceType.Agents:
        ManagedDevice = drive.Drive(Portal=Portal, base=base)
    elif device.deviceType == "Mobile":
        return device
    else:
        return device

    ManagedDevice.__dict__.update(device.__dict__.copy())

    return ManagedDevice
