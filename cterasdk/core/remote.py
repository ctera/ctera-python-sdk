from ..objects.synchronous import drive
from .enum import DeviceType
from ..objects.synchronous import edge
from ..common import parse_base_object_ref


def remote_command(Portal, device):
    tenant = parse_base_object_ref(device.portal).name
    base = f'{Portal.ctera.baseurl}/devicecmdnew/{tenant}/{device.name}'

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
