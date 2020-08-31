def api(Portal):
    path = ''
    current_session = Portal.session()
    if current_session.authenticated() and current_session.is_local_auth() and current_session.in_tenant_context():
        path = '/portals/' + current_session.tenant()
    return Portal.base_portal_url + '/api' + path
