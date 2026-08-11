from ...core.enum import DeviceType
from ...objects.asynchronous import edge, drive
from ...common import parse_base_object_ref


def remote_command(core, device):
    tenant = parse_base_object_ref(device.portal).name
    base = f'{core.v1.ctera.baseurl}/devicecmdnew/{tenant}/{device.name}'

    ManagedDevice = None
    if device.deviceType in DeviceType.Gateways:
        ManagedDevice = edge.AsyncEdge(core=core, base=base)
    elif device.deviceType in DeviceType.Agents:
        ManagedDevice = drive.AsyncDrive(core=core, base=base)
    elif device.deviceType == "Mobile":
        return device
    else:
        return device

    ManagedDevice.__dict__.update(device.__dict__.copy())

    return ManagedDevice
