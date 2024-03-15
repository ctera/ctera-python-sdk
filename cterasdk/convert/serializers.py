import queue
import json
import copy
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from .types import XMLTypes
from ..common import Item, Object, Device


_sdk_hidden = [
    'password',
    'awsSecretKey',
    'sharedSecret',
    'passPhraseSalt',
    'encPassphrase',
    'encryptedFolderKey',
    'oldPassword',
    'newPassword',
    'secretkey',
    'activationCode',
    'masterPassword',
    'masterKey',
    'secretAccess'
]


def _to_protected_dict(o):
    ret = copy.deepcopy(o.__dict__)
    for key in _sdk_hidden:
        if key in ret:
            ret[key] = '*** The Value is Hidden by the SDK ***'
    return ret


def tojsonstr(obj, pretty_print=True, no_log=True):
    """
    Convert a Python object to a JSON string.

    :param object obj: the Python object
    :param bool pretty_print: Whether to format the JSON string, defaults to ``True``
    :param book no_log: Hide sensitive values in the log messages
    :return: JSON string of the object
    :rtype: str
    """
    indent = 5 if pretty_print else None
    if no_log:
        return json.dumps(obj, default=_to_protected_dict, indent=indent)
    return json.dumps(obj, default=lambda o: o.__dict__, indent=indent)


def toxmlstr(obj, pretty_print=False):
    """
    Convert a Python object to an XML string

    :param object obj: the Python object
    :param bool pretty_print: whether to format the XML string, defaults to ``False``
    :return: XML string of the object
    :rtype: str
    """
    if obj is None:
        return None
    xml = toxml(obj)
    if pretty_print:
        string = minidom.parseString(tostring(xml)).toprettyxml(indent="   ")
        return ''.join(string.split('\n', 1)[1:])
    return tostring(xml, 'utf-8')


def toxml(obj):  # pylint: disable=too-many-branches
    root = Item()
    root.node = None
    root.parent = None
    root.obj = obj

    q = queue.Queue()
    q.put(root)
    while not q.empty():
        item = q.get()
        if isinstance(item.obj, (str, int, float, complex, bool)):
            item.node = CreateElement(item.parent, XMLTypes.VAL)
            if isinstance(item.obj, bool):
                item.node.text = str(item.obj).lower()
            else:
                item.node.text = str(item.obj)
        elif isinstance(item.obj, list):
            item.node = CreateElement(item.parent, XMLTypes.LIST)
            for member in item.obj:
                kid = Item()
                kid.node = None
                kid.parent = item.node
                kid.obj = member
                q.put(kid)
        elif isinstance(item.obj, Device):  # db.xml
            item.node = CreateElement(item.parent, XMLTypes.DB)
            for key, value in [
                (XMLTypes.NS, item.obj.namespace),
                (XMLTypes.LOCATION, item.obj.location),
                (XMLTypes.ID, item.obj.id),
                (XMLTypes.VERSION, item.obj.version),
                (XMLTypes.FIRMWARE, item.obj.firmware)
            ]:
                if value is not None:
                    item.node.set(key, value)

            kid = Item()
            kid.node = None
            kid.parent = item.node
            kid.obj = item.obj.config
            q.put(kid)
        elif isinstance(item.obj, Object):
            item.node = CreateElement(item.parent, XMLTypes.OBJ)
            classname = item.obj.__dict__.get('_classname')  # Convert { "_classname" : "ShareConfig" }
            if classname is not None:
                item.node.set(XMLTypes.CLASS, classname)
            uuid = item.obj.__dict__.get('_uuid')  # Convert { "_uuid" : "6f0e8c79-..." }
            if uuid is not None:
                item.node.set(XMLTypes.UUID, uuid)
            for attribute_name in item.obj.__dict__:
                if attribute_name.startswith('_'):
                    continue
                att = SubElement(item.node, XMLTypes.ATT)
                att.set(XMLTypes.ID, attribute_name)
                kid = Item()
                kid.node = None
                kid.parent = att
                kid.obj = item.obj.__dict__[attribute_name]
                q.put(kid)

    return root.node


def CreateElement(parent, tag):
    if parent is not None:
        element = SubElement(parent, tag)
    else:
        element = Element(tag)
    return element
