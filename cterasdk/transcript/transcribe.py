import re

import os

from xml.dom import minidom

from xml.sax.saxutils import escape

from xml.parsers.expat import ExpatError

def transcribe(request, response = None):
    
    comment = '<!--TEMPLATE-->'
    
    filename = './CTERA_' + str(os.getpid()) + '.html'
    
    file = None
    
    if not os.path.exists(filename):
        
        template = 'C:\\Users\\saimon\\CloudDrive\\My Files\\Development\\chopincore\\cterasdk\\transcript\\apidoc.template'
        
        file = open(template, 'r').read()
        
    else:
        
        file = open(filename, 'r').read()
    
    array = file.split(comment)
    
    header = array[0]
    
    footer = array[1]
    
    #
    
    uri = request.full_url
    
    idx = re.search("https?://[^/]*", uri).end()
        
    uri = uri[idx:]
    
    if uri.endswith('?'):
        
        uri = uri[:-1]
    
    method = request.get_method()
    
    tuples = request.header_items()
    
    headers = []
    
    for key, value in tuples:
        
        if key == 'Content-type' or key == 'Cookie':
            
            headers.append((key, value))
    
    data = ''
    
    if request.data != None:
        
        data = request.data.decode('utf-8')

    file = open(filename, 'w')
    
    string = '<div style="border: 1px solid #EBECF0; margin-bottom: 10px;">'
    
    string = string + '<p class="h4">' + method + ' ' + uri + '</p>'
    
    # Request headers:
    
    if len(headers) > 0:
        
        string = string + "<br/><p class=\"h6\">Request headers:</p>"

        for key, value in headers:

            string = string + '<p>' + key + ': ' + value + '</p>'
    
    # Request body:
    
    if data:
        
        string = string + "<br/><p class=\"h6\">Request body:</p>"
        
        string = string + '<pre>' + prettify(data) + '</pre>'
        
    # Response body:
    
    if response != None:

        reply = response.read()

        if reply:

            string = string + "<br/><p class=\"h6\">Response body:</p>"

            string = string + '<pre>' + prettify(reply) + '</pre>'
        
    string = string + '</div>'
    
    file.write(header + string + comment + footer)
        
    file.close()
    
def prettify(data):
    
    try:
        
        data = minidom.parseString(data).toprettyxml(indent = "   ")

        data = ''.join(data.split('\n', 1)[1:])

        data = escape(data)

        return data

    except ExpatError:

        return data
    
