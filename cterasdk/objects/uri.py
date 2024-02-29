import urllib.parse
from pathlib import Path


def create(base, *segments):
    """
    Create a URL from a Base URL, and URL segments

    :param str base: Base URL
    :param list(str),optional segments: URL segments

    :returns: Full URL, comprised of the Base URL and URL segments
    :rtype: str
    """
    url_components = components(base)
    segments = [url_components.path, *segments]
    root = '/'
    url = Path(root)
    for segment in segments:
        segment = segment[1:] if Path(segment).is_relative_to(root) else segment
        url = url.joinpath(segment)
    url = urllib.parse.urljoin(base, url.as_posix())
    return f'{url}{root}' if segments[-1] == root else url


def components(url):
    """
    Parse a URL
    """
    return urllib.parse.urlparse(url)


def unquote(url):
    return urllib.parse.unquote(url)


def quote(url):
    return urllib.parse.quote(url)
