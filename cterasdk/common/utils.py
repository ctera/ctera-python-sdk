import re
import logging
from datetime import datetime

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
    d3 = dict()
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
        raise ValueError("Invalid current unit type %s" % u1)
    if u2 not in data_units:
        raise ValueError("Invalid target unit type %s" % u2)
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
        raise ValueError("Invalid type '%s', expected 'datetime'" % type(time))
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
        raise ValueError('Invalid day of week: %s' % day)
    return name


class BaseObjectRef(Object):
    """
    Class Representing a Portal Base Object Reference

    :ivar str classname: Base object class name
    :ivar str uid: Base object unique identifier (uid)
    :ivar str tenant: Base object tenant name
    :ivar str name: Base object name
    """
    def __init__(self, classname, uid, tenant, name):
        """
        :param str classname: Base object class name
        :param str uid: Base object unique identifier
        :param str tenant: Base object tenant
        :param str name: Base object name
        """
        self.classname = classname
        self.uid = uid
        self.tenant = tenant
        self.name = name

    def in_tenant_context(self):
        """
        Returns True if the base object exists in a context of a tenant
        """
        return bool(self.tenant)

    def __str__(self):
        """
        Returns a string representation of the base object reference
        """
        return '/'.join(['objs', self.uid, self.tenant, self.classname, self.name])


def parse_base_object_ref(base_object_ref):
    """
    Parse a base object reference.

    :param str base_object_ref: Base object reference
    :return cterasdk.common.utils.BaseObjectRef: Object holding the classname, uid, tenant and object name
    """
    regex = '^objs/[1-9][0-9]*/[^/]*/[A-Za-z]+/.*$'
    match = re.search(regex, base_object_ref)
    if match:
        logging.getLogger().debug('Found match. %s', {'ref': base_object_ref})
        _, uid, tenant, classname, name = match.group(0).split('/')
        return BaseObjectRef(classname, uid, tenant, name)
    logging.getLogger().debug('No match found. %s', {'ref': base_object_ref})
    return None
