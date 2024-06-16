import json
import queue
import logging
from xml.etree.ElementTree import fromstring, ParseError

from .types import XMLTypes
from ..common import Item, Object, Device


def ParseValue(data):

    if data is None:
        return ''

    try:
        if "." in data:
            return float(data)
    except ValueError:
        pass

    try:
        return int(data)
    except ValueError:
        pass

    text = data.strip()
    if text == "true":
        return True
    if text == "false":
        return False

    return text


def SetAppendValue(item, value):
    if item.parent is not None:
        if isinstance(item.parent.value, list):
            item.parent.value.append(value)
        else:
            setattr(item.parent.value, item.id, value)
    else:
        item.value = value


def fromjsonstr(fromstr):
    if not fromstr:
        return fromstr

    root = Item()
    try:
        root.node = json.loads(fromstr)
    except json.decoder.JSONDecodeError:
        logging.getLogger('cterasdk.convert').debug('Parsing failed. Expected JSON format but received invalid input.')
        return None
    root.parent = None
    root.value = None

    q = queue.Queue()
    q.put(root)
    while not q.empty():
        item = q.get()
        if item.node is None:
            SetAppendValue(item, None)
        elif isinstance(item.node, (int, float, bool, str)):
            SetAppendValue(item, item.node)
        elif isinstance(item.node, list):
            item.value = []
            SetAppendValue(item, item.value)
            for kidnode in item.node:
                kid = Item()
                kid.parent = item
                kid.node = kidnode
                q.put(kid)
        elif isinstance(item.node, dict):
            item.value = Object()
            SetAppendValue(item, item.value)
            for kidnode, kidvalue in item.node.items():
                kid = Item()
                kid.parent = item
                kid.id = kidnode
                kid.node = kidvalue
                q.put(kid)

    return root.value


def fromxmlstr(string):  # pylint: disable=too-many-branches,too-many-statements

    if not string:
        logging.getLogger('cterasdk.convert').debug('Empty payload received.')

    root = Item()
    root.value = None
    root.parent = None

    try:
        root.node = fromstring(string)
    except ParseError:
        logging.getLogger('cterasdk.convert').debug('Parsing failed. Expected XML format but received invalid input.')
        return None

    q = queue.Queue()
    q.put(root)
    while not q.empty():
        item = q.get()
        if item.node.tag == XMLTypes.VAL:
            value = ParseValue(item.node.text)
            SetAppendValue(item, value)
        elif item.node.tag == XMLTypes.LIST:
            item.value = []
            SetAppendValue(item, item.value)
            for kidnode in item.node:
                if kidnode.tag in [XMLTypes.OBJ, XMLTypes.VAL]:
                    kid = Item()
                    kid.parent = item
                    kid.node = kidnode
                    q.put(kid)
        elif item.node.tag == XMLTypes.OBJ:
            classname = item.node.attrib.get(XMLTypes.CLASS)
            uuid = item.node.attrib.get(XMLTypes.UUID)

            item.value = Object()
            if classname is not None:  # Convert <obj class="ShareConfig"> to { "_classname" : "ShareConfig" }
                item.value._classname = classname  # pylint: disable=protected-access
            if uuid is not None:  # Convert <obj uuid="6f0e8c79-..."> to { "_uuid" : "6f0e8c79-..." }
                item.value._uuid = uuid  # pylint: disable=protected-access

            SetAppendValue(item, item.value)

            for kidnode in item.node:
                if kidnode.tag == XMLTypes.ATT:
                    kid = Item()
                    kid.id = kidnode.attrib[XMLTypes.ID]
                    kid.parent = item
                    kid.node = kidnode
                    q.put(kid)
        elif item.node.tag == XMLTypes.ATT:
            if len(item.node) > 0:
                for kidnode in item.node:
                    if kidnode.tag in [XMLTypes.OBJ, XMLTypes.LIST, XMLTypes.VAL]:
                        kid = Item()
                        kid.id = item.id
                        kid.parent = item.parent
                        kid.node = kidnode
                        q.put(kid)
            else:
                SetAppendValue(item, None)              # include empty attrs
        elif item.node.tag == XMLTypes.DB:              # db.xml
            item.value = Device(
                item.node.attrib.get(XMLTypes.ID),
                item.node.attrib.get(XMLTypes.VERSION),
                item.node.attrib.get(XMLTypes.FIRMWARE)
            )
            SetAppendValue(item, item.value)

            kid = Item()
            kid.id = item.node.attrib.get(XMLTypes.ID)
            kid.parent = item
            kid.node = list(item.node)[0]
            q.put(kid)

    return root.value
