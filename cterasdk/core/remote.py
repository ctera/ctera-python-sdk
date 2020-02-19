from ..common import Object

from ..object import Gateway, Agent

from .enum import DeviceType

import logging

def remote_command(Portal, device):
    
    port = Portal.port()
        
    https = Portal.https()
    
    ManagedDevice = None
    
    if device.deviceType in DeviceType.Gateways:
        
        ManagedDevice = Gateway.Gateway(host = device.name, port = port, https = https, Portal = Portal)
        
    elif device.deviceType in DeviceType.Agents:
        
        ManagedDevice = Agent.Agent(host = device.name, port = port, https = https, Portal = Portal)
        
    elif device.deviceType == "Mobile":
        
        return device
    
    else:
        
        return device
    
    ManagedDevice.__dict__.update(device.__dict__.copy())
    
    return ManagedDevice