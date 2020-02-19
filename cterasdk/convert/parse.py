from .exception import ParseException

from ..common import Item, Object

from xml.etree.ElementTree import fromstring, ParseError

import queue, json

import logging

def ParseValue(data):
    
    try:
        
        if not data:
            
            return data

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
    
    elif text == "false":
        
        return False

    else:

        return text
    
def SetAppendValue(item, value):    
    
    if item.parent != None:
        
        if type(item.parent.value) == list:
            
            item.parent.value.append(value)
        
        else:
            
            setattr(item.parent.value, item.id, value)
            
        return
    
    item.value = value

def fromjsonstr(fromstring):
    
    # Check if fromstring is empty
    
    if not fromstring:
        
        return fromstring
    
    root = Item()
    
    root.node = json.loads(fromstring)
    
    root.parent = None
    
    root.value = None
    
    q = queue.Queue()
    
    q.put(root)
    
    while not q.empty():

        item = q.get()
        
        if item.node == None:
            
            SetAppendValue(item, None)
        
        if type(item.node) in [int, float, bool, str]:

            SetAppendValue(item, item.node)
            
        if type(item.node) == list:
            
            item.value = []
            
            SetAppendValue(item, item.value)
            
            for kidnode in item.node:
                
                kid = Item()
                    
                kid.parent = item

                kid.node = kidnode

                q.put(kid)
                
        if type(item.node) == dict:
            
            item.value = Object()
            
            SetAppendValue(item, item.value)
            
            for kidnode, kidvalue in item.node.items():
                
                kid = Item()
                    
                kid.parent = item
                
                kid.id = kidnode

                kid.node = kidvalue

                q.put(kid)
        
    return root.value

def fromxmlstr(string):
    
    string = string.decode('utf-8')
    
    # Check for empty string
    
    if not string:
        
        logging.getLogger().debug('Skipping.')
        
        return string
    
    # Do not attempt to parse HTML
    
    if string.startswith('<!DOCTYPE HTML>'):
        
        logging.getLogger().debug('Skipping. {0}'.format({'type' : 'HTML'}))
        
        return string
    
    OBJ     = 'obj'
    
    ATT     = 'att'
    
    VAL     = 'val'
    
    LIST    = 'list'
    
    ID      = 'id'
    
    CLASS   = 'class'
    
    UUID    = 'uuid'
    
    root = Item()
    
    root.value = None
    
    root.parent = None
    
    try:
    
        root.node = fromstring(string)
        
    except ParseError as e:
        
        raise ParseException()
    
    q = queue.Queue()
    
    q.put(root)
    
    while not q.empty():
        
        item = q.get()
    
        if item.node.tag == VAL:
            
            value = ParseValue(item.node.text)
            
            SetAppendValue(item, value)
                
        if item.node.tag == LIST:
            
            item.value = []
            
            SetAppendValue(item, item.value)
            
            for kidnode in item.node:
                
                if kidnode.tag in [OBJ, VAL]:
                    
                    kid = Item()
                    
                    kid.parent = item
                    
                    kid.node = kidnode
                    
                    q.put(kid)
                    
        if item.node.tag == OBJ:
            
            classname = item.node.attrib.get(CLASS)
            
            uuid = item.node.attrib.get(UUID)
                                    
            item.value = Object()
            
            if classname != None:                   # Convert <obj class="ShareConfig"> to { "_classname" : "ShareConfig" }
            
                item.value._classname = classname
                
            if uuid != None:                        # Convert <obj uuid="6f0e8c79-..."> to { "_uuid" : "6f0e8c79-..." }
                
                item.value._uuid = uuid
            
            SetAppendValue(item, item.value)
            
            for kidnode in item.node:
                
                if kidnode.tag == ATT:
                    
                    kid = Item()
                    
                    kid.id = kidnode.attrib[ID]
                    
                    kid.parent = item
                    
                    kid.node = kidnode
                    
                    q.put(kid)
                    
        if item.node.tag == ATT:
            
            if len(item.node) > 0:
            
                for kidnode in item.node:

                    if kidnode.tag in [OBJ, LIST, VAL]:

                        kid = Item()

                        kid.id = item.id

                        kid.parent = item.parent

                        kid.node = kidnode

                        q.put(kid)
                        
            else:

                SetAppendValue(item, None)              # include empty attrs

    return root.value