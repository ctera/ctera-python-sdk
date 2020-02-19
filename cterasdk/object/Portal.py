from ..client import NetworkHost, CTERAHost

from ..core import *

class Portal(CTERAHost):
    
    def __init__(self, host, port, https):
        
        super().__init__(host, port, https)
        
        session.inactive_session(self)
        
    def test(self):
        
        connection.test(self)
        
        return CTERAHost.get(self, self._baseurl(), '/public/publicInfo', params = {})
        
    def login(self, username, password):
        
        login.login(self, username, password)
        
    @decorator.authenticated
    def logout(self):
        
        login.logout(self)
        
    def whoami(self):
        
        whoami.whoami(self)
        
    @decorator.authenticated
    def get(self, path, params = {}):
        
        return super().get(self._api(), path, params)
    
    @decorator.authenticated
    def show(self, path):
        
        super().show(self._api(), path)
    
    @decorator.authenticated
    def get_multi(self, path, paths):
        
        return super().get_multi(self._api(), path, paths)
    
    @decorator.authenticated
    def show_multi(self, paths):
        
        super().show_multi(self._api(), paths)
        
    @decorator.update_current_tenant
    @decorator.authenticated
    def put(self, path, value):
        
        return super().put(self._api(), path, value)
    
    def form_data(self, path, form_data):
        
        return super().form_data(self._api(), path, form_data)
        
    @decorator.authenticated
    def execute(self, path, name, param = None):
        
        return super().execute(self._api(), path, name, param)
    
    @decorator.authenticated
    def query(self, path, param):
        
        return query.query(self, path, param)
    
    @decorator.authenticated
    def show_query(self, path, param):
        
        return query.show(self, path, param)
    
    @decorator.authenticated
    def add(self, path, param):
        
        return super().add(self._api(), path, param)

    def iterator(self, path, param):
        
        return query.iterator(self, path, param)
    
    def local_users(self, include = []):
        
        return users.local_users(self, include)
    
    def add_user(self, username, email, first_name, last_name, password, role = enum.Role.EndUser, company = None, comment = None):
        
        return users.add(self, username, email, first_name, last_name, password, role, company, comment)
    
    def delete_user(self, username):
        
        return users.delete(self, username)
        
    def domains(self):
        
        return self.get('/domains')
    
    def domain_users(self, domain, include = []):
        
        return users.domain_users(self, domain, include)
    
    def fetch(self, tuples):
        
        return directoryservice.fetch(self, tuples)
    
    def device(self, name, include = []):
        
        return devices.device(self, name, include)
    
    def filers(self, include = [], allPortals = False, deviceTypes = []):
        
        return devices.filers(self, include, allPortals, deviceTypes)
    
    def agents(self, include = [], allPortals = False):
        
        return devices.agents(self, include, allPortals)
    
    def server_agents(self, include = [], allPortals = False):
        
        return devices.servers(self, include, allPortals)
    
    def desktop_agents(self, include = [], allPortals = False):
        
        return devices.desktops(self, include, allPortals)
    
    def devices_by_name(self, names, include = []):
        
        return devices.by_name(self, include, names)
    
    def devices(self, include = [], allPortals = False, filters = []):
        
        return devices.devices(self, include, allPortals, filters)
    
    def generate_code(self, username, tenant = None):
        
        return activation.generate_code(self, username, tenant)
    
    def cloudfs(self):
        
        return cloudfs.CloudFS(self)
    
    def zones(self):
        
        return zones.Zones(self)
    
    def files(self):
        
        return files.FileBrowser(self)
        
    def logs(self, topic = enum.LogTopic.System, minSeverity = enum.Severity.INFO, originType = enum.OriginType.Portal, before = None, after = None):

        return logs.logs(self, topic, minSeverity, originType, before, after)
    
    def _api(self):
        
        return self._baseurl() + '/api'
        
class GlobalAdmin(Portal):
    
    def __init__(self, host, port = 443, https = True):
        
        super().__init__(host, port, https)
        
    def browse_tenant(self, tenant_name):
        
        portals.browse(self, tenant_name)
        
    def browse_global_admin(self):
        
        self.browse_tenant('')
    
    def servers(self, include = []):
        
        return servers.servers(self, include)
    
    def tenants(self):
        
        return portals.portals(self)
    
    def tenants(self, include_deleted = False):
        
        return portals.portals(self, include_deleted)
    
    def add_tenant(self, name, display_name = None, billing_id = None, company = None):
        
        return portals.add(self, name, display_name, billing_id, company)
        
    def delete_tenant(self, name):
        
        return portals.delete(self, name)
        
    def undelete_tenant(self, name):
        
        return portals.undelete(self, name)
    
    def _files(self):
        
        return '/admin/webdav/Users'
        
    def _baseurl(self):
        
        return NetworkHost.baseurl(self) + '/' + self._context()
    
    def _context(self):
        
        return 'admin'
        
class ServicesPortal(Portal):
    
    def __init__(self, host, port = 443, https = True):
        
        super().__init__(host, port, https)
        
    def _files(self):
        
        return '/ServicesPortal/webdav'
        
    def _baseurl(self):
        
        return NetworkHost.baseurl(self) + '/' + self._context()
    
    def _context(self):
        
        return 'ServicesPortal'