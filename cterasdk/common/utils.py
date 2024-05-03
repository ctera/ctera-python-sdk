import re
import socket
import logging
import ipaddress

from datetime import datetime
from packaging.version import parse as parse_version

from .object import Object
from .enum import DayOfWeek


def union(g1, g2):
    """
    Create a union of two lists, without duplicates.

    :return list: the union of the two lists
    """
    return g1 + list(set(g2) - set(g1))


def merge(d1, d2):
    """
    Merge two dictionaries. In case of duplicate keys, this function will return values from the 2nd dictionary

    :return dict: the merged dictionary
    """
    d3 = {}
    if d1:
        d3.update(d1)
    if d2:
        d3.update(d2)
    return d3


class DataUnit:
    """
    Data Unit

    :ivar str PB: Petabytes
    :ivar str TB: Terabytes
    :ivar str GB: Gigabytes
    :ivar str MB: Megabytes
    :ivar str KB: Kilobytes
    :ivar str B: Bytes
    """
    PB = 'PB'
    TB = 'TB'
    GB = 'GB'
    MB = 'MB'
    KB = 'KB'
    B = 'B'


def convert_size(numeric, u1, u2):
    """
    Convert size between data units

    :param str u1: Convert from data unit
    :param str u2: Convert to data unit
    """
    data_units = [DataUnit.B, DataUnit.KB, DataUnit.MB, DataUnit.GB, DataUnit.TB, DataUnit.PB]
    if u1 not in data_units:
        raise ValueError(f"Invalid current unit type {u1}")
    if u2 not in data_units:
        raise ValueError(f"Invalid target unit type {u2}")
    offset = (data_units.index(u1) - data_units.index(u2)) * 10
    if offset > 0:
        return numeric * (1 << offset)
    if offset < 0:
        return numeric / (1 << abs(offset))
    return numeric


def df_military_time(time):
    """
    Format datetime object to military time

    :param datetime.datetime datetime: Datetime object to convert
    :returns: Military time formatted string
    :rtype: str
    """
    if not isinstance(time, datetime):
        raise ValueError(f"Invalid type '{type(time)}', expected 'datetime'")
    return time.strftime('%H:%M:%S')


def day_of_week(day):
    """
    Interpret the day of week from numeric to str

    :param int day: A numeric integer representing the day of week
    :returns: Name of the day
    :rtype: str
    """
    name = {v: k for k, v in DayOfWeek.__dict__.items() if isinstance(v, int)}.get(day)
    if not name:
        raise ValueError(f'Invalid day of week: {day}')
    return name


class BaseObjectRef(Object):
    """
    Class Representing a Portal Base Object Reference

    :ivar str classname: Base object class name
    :ivar str uid: Base object unique identifier (uid)
    :ivar str tenant: Base object tenant name
    :ivar str name: Base object name
    """
    def __init__(self, uid, tenant=None, classname=None, name=None, more=None):
        """
        :param str uid: Base object unique identifier
        :param str,optional tenant: Base object tenant
        :param str,optional classname: Base object class name
        :param str,optional name: Base object name
        :param str,optional more: Base object more info
        """
        self.uid = uid
        self.tenant = tenant
        self.classname = classname
        self.name = name
        self.more = more

    def in_tenant_context(self):
        """
        Returns True if the base object exists in a context of a tenant
        """
        return bool(self.tenant)

    def __str__(self):
        """
        Returns a string representation of the base object reference
        """
        return '/'.join(['objs', self.uid, self.tenant or '', self.classname or '', self.name or '', self.more or ''])


def parse_base_object_ref(base_object_ref):
    if not base_object_ref.startswith('objs/'):
        logging.getLogger('cterasdk.common').error('Invalid base object reference. %s', {'ref': base_object_ref})
        return None
    base_object_ref = base_object_ref[5:]
    p = re.compile('[^/]*')
    components = ['uid', 'tenant', 'classname', 'name', 'more']
    arguments = {}
    while base_object_ref:
        match = p.match(base_object_ref)
        arguments[components.pop(0)] = match.group()
        base_object_ref = base_object_ref[match.end() + 1:]
    return BaseObjectRef(**arguments)


def parse_to_ipaddress(address):
    """
    Parse an ip or network address into ipaddress object

    :param str address: ip (10.0.0.5) or network address (192.168.44.0/28)
    :return: ipaddress.IPV4Address/IPV6Address or ipaddress.IPV4Network/IPV6Network
    """
    try:
        try:
            ip_addrr = ipaddress.ip_address(address)
            logging.getLogger('cterasdk.common').debug('ip address validated. %s', {'ip': str(ip_addrr)})
            return ip_addrr
        except (ValueError, TypeError):
            ip_network = ipaddress.ip_network(address)
            logging.getLogger('cterasdk.common').debug('ip network validated. %s', {'network': str(ip_network)})
            return ip_network
    except (ValueError, TypeError):
        err = ValueError(f'{address} does not appear to be an IPv4 or IPv6 network or ip address')
        logging.getLogger('cterasdk.common').error('Incorrect entry, please use IPv4 or IPv6 CIDR Formats. %s', {'Error': err})
        raise err


class Version:
    """Software Version"""

    def __init__(self, version):
        self._version = parse_version(version)

    def __eq__(self, v):
        return self._version == parse_version(v)

    def __gt__(self, v):
        return self._version > parse_version(v)

    def __ge__(self, v):
        return self._version >= parse_version(v)

    def __lt__(self, v):
        return self._version < parse_version(v)

    def __le__(self, v):
        return self._version <= parse_version(v)

    def __ne__(self, v):
        return self._version != parse_version(v)

    @property
    def version(self):
        return str(self._version)

    def __str__(self):
        return self.version


def utf8_decode(message):
    """
    Decode UTF-8 String
    """
    return message.decode('utf-8')


def tcp_connect(host, port):
    logging.getLogger('cterasdk.common').debug('Testing connection. %s', {'host': host, 'port': port})
    message = f"Connection error to remote host {host} on port {port}."
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rc = None
    try:
        rc = sock.connect_ex((host, port))
    except socket.gaierror:
        logging.getLogger('cterasdk.common').debug(message)
        raise ConnectionError(message)

    if rc != 0:
        logging.getLogger('cterasdk.common').debug(message)
        raise ConnectionError(message)
    logging.getLogger('cterasdk.common').debug("Connection established to remote host %s on port %s", host, port)
