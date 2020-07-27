import re
import os
import pathlib
from xml.dom import minidom
from xml.sax.saxutils import escape
from xml.parsers.expat import ExpatError


class Transcribe():
    COMMENT = '<!--TEMPLATE-->'
    SECTION_START = '<div style="border: 1px solid #EBECF0; margin-bottom: 10px;">'
    SECTION_END = '</div>'
    RECORDED_HEADERS = ['content-type', 'cookie']

    def __init__(self):
        self._filename = './CTERA_' + str(os.getpid()) + '.html'

    def transcribe(self, request, response=None):
        self._append_content(self._get_content(request, response))

    @classmethod
    def _get_content(cls, request, response):
        return ''.join(
            [
                Transcribe.SECTION_START,
                cls._get_request_content(request),
                cls._get_response_content(response) if response else '',
                Transcribe.SECTION_END
            ]
        )

    @classmethod
    def _get_request_content(cls, request):
        request_content_array = [
            '<p class="h4">' + request.method + ' ' + cls._parse_url(request.url) + '</p>'
        ]

        # Request headers:
        headers = cls._get_headers_array(request.headers)
        if len(headers) > 0:
            request_content_array.append("<br/><p class=\"h6\">Request headers:</p>")
            for key, value in headers:
                request_content_array.append('<p>' + key + ': ' + value + '</p>')

        # Request body:
        if request.body:
            request_content_array.append("<br/><p class=\"h6\">Request body:</p>")
            request_content_array.append('<pre>' + cls._prettify(request.body.decode('utf-8')) + '</pre>')

        return ''.join(request_content_array)

    @staticmethod
    def _parse_url(url):
        uri = url[re.search("https?://[^/]*", url).end():]
        return uri[:-1] if uri.endswith('?') else uri

    @classmethod
    def _get_headers_array(cls, request_headers):
        return [
            (key, value) for key, value in request_headers.items() if key.lower() in cls.RECORDED_HEADERS
        ]

    @classmethod
    def _get_response_content(cls, response):
        response_content_array = []
        reply = response.read()
        if reply:
            response_content_array.append("<br/><p class=\"h6\">Response body:</p>")
            response_content_array.append('<pre>' + cls._prettify(reply) + '</pre>')
        return ''.join(response_content_array)

    def _append_content(self, content):
        header, footer = self._get_header_footer()
        with open(self._filename, 'w') as f:
            f.write(header + content + Transcribe.COMMENT + footer)

    def _get_header_footer(self):
        filename = self._filename if os.path.exists(self._filename) else \
            os.path.join(pathlib.Path(__file__).parent.absolute(), 'apidoc.template')
        with open(filename, 'r') as f:
            content = f.read()
        array = content.split(Transcribe.COMMENT)
        return array[0], array[1]

    @staticmethod
    def _prettify(data):
        try:
            data = minidom.parseString(data).toprettyxml(indent="   ")
            data = ''.join(data.split('\n', 1)[1:])
            data = escape(data)
            return data
        except ExpatError:
            return data


def transcribe(request, response=None):
    Transcribe().transcribe(request, response)
