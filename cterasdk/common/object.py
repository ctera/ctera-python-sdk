import re
import json
import logging
from collections.abc import MutableMapping


logger = logging.getLogger('cterasdk.common')


class Object(MutableMapping):  # pylint: disable=too-many-instance-attributes

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=5)

    def __repr__(self):
        return str(self)


class Device(Object):

    def __init__(self, uid, version, firmware):
        super().__init__()
        self.namespace = 'http://www.w3.org/2001/XMLSchema-instance'
        self.location = '../../db/resources/db.xsd'
        self.id = uid
        self.version = version
        self.firmware = firmware


def delete_attrs(obj, paths):
    """
    Delete attributes

    :param cterasdk.common.object.Object object: The object
    :param list[str] paths: List of attributes to remove

    :returns: The modified object
    :rtype: cterasdk.common.object.Object
    """
    for path in paths:
        delete_attr(obj, path)


def delete_attr(obj, path):
    """
    Delete attribute

    :param cterasdk.common.object.Object object: The object
    :param str path: Attribute path

    :returns: The modified object
    :rtype: cterasdk.common.object.Object
    """
    parts = re.findall('[^/]+', path)
    parent = find_attr(obj, parts[:-1])
    remove_attr(parent, parts[-1])

    if len(parts) > 1 and isinstance(parent, Object) and not parent.__dict__:
        grandparent = find_attr(obj, parts[:-2])
        setattr(grandparent, parts[-2], None)


def find_attr(obj, path):
    """
    Find attribute

    :param cterasdk.common.object.Object object: The object
    :param str path: A string or an array of the attribute path

    :returns: The attribute, or ``None`` if not found
    """
    parts = re.findall('[^/]+', path) if isinstance(path, str) else path

    attr = obj
    for part in parts:
        attr = get_attr(attr, part)
        if attr is None:
            logger.warning('Could not find attribute. %s', {'path': f'/{"/".join(parts)}'})
            return attr
    return attr


def get_attr(obj, attr):
    """
    Get attribute

    :param cterasdk.common.object.Object object: The object
    :param str attr: The name of the attribute to retrieve

    :returns: The attribute, or ``None`` if not found
    """
    if isinstance(obj, list):
        try:
            attr = int(attr)
            return obj[attr]
        except ValueError:
            logger.warning('Could not find attribute.')
            return None

    return getattr(obj, attr, None)


def remove_attr(obj, attr):
    """
    Remove attribute

    :param cterasdk.common.object.Object object: The object
    :param str attr: The name of the attribute to remove
    """
    if isinstance(obj, list):
        remove_array_element(obj, attr)
    else:
        try:
            delattr(obj, attr)
        except AttributeError:
            logger.warning('Failed to remove attribute. Attribute not found. %s', {'attr': attr})


def remove_array_element(array, attr):

    try:
        attr = int(attr)
        if attr <= len(array) - 1:
            array.pop(attr)
        else:
            logger.warning('Could not remove array item. Index out of range. %s', {'index': attr})
    except ValueError:
        pass

    if remove_array_element_by_key(array, '_uuid', attr):
        return

    remove_array_element_by_key(array, 'name', attr)


def remove_array_element_by_key(array, key, value):
    for index, element in enumerate(array):
        element_value = getattr(element, key, None)
        if element_value == value:
            return array.pop(index)
    return None
