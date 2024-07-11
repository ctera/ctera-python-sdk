from . import uri


def edge(ctera_session, url):
    if ctera_session.connecting or \
       ctera_session.connected or \
       uri.components(url).path.endswith(_edge_no_session_resources()):
        return True
    return False


def core(ctera_session, url, context):
    if ctera_session.connecting or \
       ctera_session.connected or \
       uri.components(url).path.startswith(_core_no_session_resources(context)):
        return True
    return False


def _edge_no_session_resources():
    return _no_session_resources('', '/admingui/api/login', '/ssologin', '/api/nosession/logininfo',
                                 '/api/nosession/createfirstuser', '/migration/rest/v1/auth/user')


def _core_no_session_resources(context):
    return _no_session_resources(context, '/api/login', '/public', '/setup', '/startup')


def _no_session_resources(context, *paths):
    return tuple(uri.create(context, path) for path in paths)
