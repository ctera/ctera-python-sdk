import re
import logging

from .object import Object


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
    regex = '^objs/[1-9][0-9]+/[^/]*/[A-Za-z]+/.*$'
    match = re.search(regex, base_object_ref)
    if match:
        logging.getLogger().debug('Found match. %s', {'ref': base_object_ref})
        _, uid, tenant, classname, name = match.group(0).split('/')
        return BaseObjectRef(classname, uid, tenant, name)
    logging.getLogger().debug('No match found. %s', {'ref': base_object_ref})
    return None
