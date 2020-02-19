from ..common import Item, Object

import queue, json

from xml.etree.ElementTree import Element, SubElement, tostring

from xml.dom import minidom

def tojsonstr(obj, pretty_print = True):
    
    if pretty_print:
    
        return json.dumps(obj, default = lambda o: o.__dict__, indent = 5)
    
    else:
        
        return json.dumps(obj, default = lambda o: o.__dict__)
    
def toxmlstr(obj, pretty_print = False):
    
    if obj == None:
        
        return None
    
    xml = toxml(obj)
    
    if pretty_print:
        
        string = minidom.parseString(tostring(xml)).toprettyxml(indent = "   ")

        return ''.join(string.split('\n', 1)[1:])
    
    else:
        
        return tostring(xml)
    
def toxml(obj):
    
    OBJ     = 'obj'
    
    ATT     = 'att'
    
    VAL     = 'val'
    
    LIST    = 'list'
    
    ID      = 'id'
    
    CLASS      = 'class'
    
    UUID      = 'uuid'
    
    #
    
    root = Item()
    
    root.node = None
    
    root.parent = None
    
    root.obj = obj
    
    q = queue.Queue()
    
    q.put(root)
    
    while not q.empty():
        
        item = q.get()
    
        if type(item.obj) in [str, int, float, complex]:
            
            item.node = CreateElement(item.parent, VAL)

            item.node.text = str(item.obj)

        if type(item.obj) == bool:
            
            item.node = CreateElement(item.parent, VAL)

            item.node.text = str(item.obj).lower()
            
        if type(item.obj) == list:
            
            item.node = CreateElement(item.parent, LIST)
            
            for member in item.obj:
                
                kid = Item()
                
                kid.node = None
                
                kid.parent = item.node
                
                kid.obj = member
                
                q.put(kid)
                
        if isinstance(item.obj, Object):
            
            item.node = CreateElement(item.parent, OBJ)
                
            classname = item.obj.__dict__.get('_classname')     # Convert { "_classname" : "ShareConfig" }
            
            if classname != None:
                
                item.node.set(CLASS, classname)
                
            uuid = item.obj.__dict__.get('_uuid')               # Convert { "_uuid" : "6f0e8c79-..." }
            
            if uuid != None:
                
                item.node.set(UUID, uuid)
            
            for attribute_name in item.obj.__dict__:
                
                if attribute_name.startswith('_'):
                    
                    continue
                
                att = SubElement(item.node, ATT)
                
                att.set(ID, attribute_name)
                
                kid = Item()
                
                kid.node = None
                
                kid.parent = att
                
                kid.obj = item.obj.__dict__[attribute_name]
                
                q.put(kid)
        
    return root.node

def CreateElement(parent, tag):
    
    if parent != None:
        
        element = SubElement(parent, tag)

    else:

        element = Element(tag)
        
    return element