from ..client import NetworkHost, CTERAHost

from ..edge import *

from ..edge.enum import *
    
class Gateway(CTERAHost):
    
    def __init__(self, host, port = 80, https = False, Portal = None):
        
        super().__init__(host, port, https)
        
        self._remote_access = False
        
        if Portal != None:
            
            self._Portal = Portal
            
            self._ctera_client   = Portal._ctera_client
            
            session.start_remote_session(self, Portal)
            
        else:
            
            session.inactive_session(self)
    
    def test(self):

        return connection.test(self)
    
    def login(self, username, password):

        login.login(self, username, password)
        
    @decorator.authenticated
    def logout(self):

        login.logout(self)
        
    def whoami(self):
        
        whoami.whoami(self)
    
    def remote_access(self):
        
        remote.remote_access(self, self._Portal)
    
    @decorator.authenticated
    def get(self, path, params = {}):
        
        return super().get(self._api(), path, params)
    
    @decorator.authenticated
    def show(self, path):
        
        super().show(self._api(), path)
    
    @decorator.authenticated
    def get_multi(self, paths):
        
        return super().get_multi(self._api(), '', paths)
    
    @decorator.authenticated
    def show_multi(self, paths):
        
        super().show_multi(self._api(), paths)
        
    @decorator.authenticated
    def put(self, path, value):
        
        return super().put(self._api(), path, value)
    
    @decorator.authenticated
    def post(self, path, value):
        
        return super().post(self._api(), path, value)
    
    def form_data(self, path, form_data):
        
        return super().form_data(self._api(), path, form_data)
    
    @decorator.authenticated
    def execute(self, path, name, param = None):
        
        return super().execute(self._api(), path, name, param)
    
    @decorator.authenticated
    def query(self, path, key, value):
        
        return query.query(self, path, key, value)
    
    @decorator.authenticated
    def show_query(self, path, key, value):
        
        query.show(self, path, key, value)
    
    @decorator.authenticated
    def add(self, path, param):
        
        return super().add(self._api(), path, param)
    
    @decorator.authenticated
    def delete(self, path):
        
        return super().delete(self._api(), path)
    
    @decorator.authenticated
    def rm(self, path):
        
        return super().delete(self._files(), path)
        
    def location(self):
        
        return config.location(self)
                
    def set_location(self, location):

        config.set_location(self, location)
        
    def hostname(self):
        
        return config.hostname(self)

    def set_hostname(self, hostname):

        config.set_hostname(self, hostname)
    
    def set_static_ipaddr(self, address, subnet, gateway, DNSServer1, DNSServer2 = None):

        network.set_static_ipaddr(self, address, subnet, gateway, DNSServer1, DNSServer2)
    
    def set_static_nameserver(self, DNSServer1, DNSServer2 = None):

        network.set_static_nameserver(self, DNSServer1, DNSServer2)
        
    def enable_dhcp(self):

        network.enable_dhcp(self)
    
    def tcp_connect(self, address, port):

        return network.tcp_connect(self, address, port)
    
    def connect(self, server, user, password, license = License.EV16):
        
        services.connect(self, server, user, password, license)
        
    def activate(self, server, user, code, license = License.EV16):

        services.activate(self, server, user, code, license)
        
    def apply_license(self, license):
        
        licenses.apply(self, license)
        
    def reconnect(self):

        services.reconnect(self)
        
    def disconnect(self):

        services.disconnect(self)
        
    def enable_sso(self):

        services.enable_sso(self)
        
    def domains(self):
        
        return directoryservice.domains(self)
        
    def advanced_mapping(self, domain, start, end):
        
        directoryservice.advanced_mapping(self, domain, start, end)
    
    def directory_services_connect(self, domain, username, password, ou = None):

        directoryservice.connect(self, domain, username, password, ou)
        
    def directory_services_disconnect(self):

        directoryservice.disconnect(self)
    
    def enable_telnet(self, code):
 
        telnet.enable(self, code)
        
    def disable_telnet(self):

        telnet.disable(self)
        
    def enable_syslog(self, server, port = 514, proto = IPProtocol.UDP, minSeverity = Severity.INFO):

        syslog.enable(self, server, port, proto, minSeverity)
        
    def disable_syslog(self):

        syslog.disable(self)
        
    def enable_audit_logs(self, path, auditEvents = [AuditEvents.CreateFilesWriteData, AuditEvents.CreateFoldersAppendData, AuditEvents.WriteExtendedAttributes, AuditEvents.DeleteSubfoldersAndFiles, AuditEvents.WriteAttributes, AuditEvents.Delete, AuditEvents.ChangePermissions, AuditEvents.ChangeOwner], logKeepPeriod = 30, maxLogKBSize = 102400, maxRotateTime = 1440, includeAuditLogTag = True, humanReadableAuditLog = False):

        audit.enable(self, path, auditEvents, logKeepPeriod, maxLogKBSize, maxRotateTime, includeAuditLogTag, humanReadableAuditLog)
        
    def disable_audit_logs(self):

        audit.disable(self)
        
    def enable_mail_server(self, SMTPServer, port = 25, username = None, password = None, useTLS = True):

        mail.enable(self, SMTPServer, port, username, password, useTLS)
        
    def disable_mail_server(self):
 
        mail.disable(self)
        
    def configure_backup(self, passphrase = None):
        
        backup.configure_backup(self, passphrase)

    def start_backup(self):

        backup.start(self)
        
    def suspend_backup(self):

        backup.suspend(self)
        
    def unsuspend_backup(self):

        backup.unsuspend(self)
        
    def suspend_sync(self):

        sync.suspend(self)
        
    def unsuspend_sync(self):

        sync.unsuspend(self)
        
    def refresh_cloud_folders(self):

        sync.refresh(self)
        
    def enable_caching(self):
 
        cache.enable(self)

    def disable_caching(self):

        cache.disable(self)

    def force_eviction(self):
  
        cache.force_eviction(self)
        
    def reboot(self, wait = False):

        power.reboot(self, wait)
        
    def shutdown(self):

        power.shutdown(self)
        
    def reset(self, wait = False):
 
        power.reset(self, wait)
        
    def add_user(self, username, password, fullName = None, email = None, uid = None):

        users.add(self, username, password, fullName, email, uid)
        
    def add_first_user(self, username, password, email = ''):

        users.add_first_user(self, username, password, email)
        
    def delete_user(self, username):

        users.delete(self, username)
        
    def add_members(self, group, members):
        
        groups.add_members(self, group, members)
        
    def remove_members(self, group, members):
        
        groups.remove_members(self, group, members)
        
    def format_drive(self, name):
  
        drive.format_drive(self, name)

    def format_all_drives(self):

        drive.format_all(self)
        
    def add_volume(self, name, size = None, fileSystemType = 'xfs', device = None, passphrase = None):

        volumes.add(self, name, size, fileSystemType, device, passphrase)
        
    def delete_volume(self, name): 

        volumes.delete(self, name)
        
    def delete_all_volumes(self):

        volumes.delete_all(self)
        
    def add_array(self, name, level, members):
        
        array.add(self, name, level, members)
        
    def delete_array(self, name):

        array.delete(self, name)
        
    def delete_all_arrays(self, name, level, members):

        array.delete_all(self)
    
    def add_share(self, name, directory, acl = [], access = Acl.WindowsNT, csc = ClientSideCaching.Manual, dirPermissions = 777, comment = None, \
                 exportToAFP = False, exportToFTP = False, exportToNFS = False, exportToPCAgent = False, exportToRSync = False, indexed = False):
        
        shares.add(self, name, directory, acl, access, csc, dirPermissions, comment, exportToAFP, exportToFTP, exportToNFS, exportToPCAgent, exportToRSync, indexed)
        
    def add_share_acl(self, name, acl):

        shares.add_acl(self, name, acl)
        
    def remove_share_acl(self, name, acl):

        shares.remove_acl(self, name, acl)
        
    def delete_share(self, name):

        shares.delete(self, name)
        
    def enable_smb(self):

        smb.enable(self)
        
    def set_packet_signing(self, mode):

        smb.set_packet_signing(self, mode)
        
    def enable_abe(self):

        smb.enable_abe(self)

    def disable_abe(self):

        smb.disable_abe(self)
        
    def disable_smb(self):

        smb.disable(self)
        
    def enable_aio(self):
        
        aio.enable(self)
        
    def disable_aio(self):
        
        aio.disable(self)
        
    def disable_ftp(self):

        ftp.disable(self)
        
    def disable_afp(self):

        afp.disable(self)
        
    def disable_nfs(self):

        nfs.disable(self)
        
    def disable_rsync(self):

        rsync.disable(self)
        
    def set_timezone(self, timezone):

        timezone.set_timezone(self, timezone)
        
    def enable_ntp(self, servers = []):

        ntp.enable(self, servers)
        
    def disable_ntp(self):

        ntp.disable(self)
    
    def logs(self, topic, include = ['severity', 'time', 'msg', 'more'], minSeverity = Severity.INFO):

        return logs.logs(self, topic, include, minSeverity)
    
    def run_shell_command(self, shell_command):

        return shell.run_shell_command(self, shell_command)
    
    def run_cli_command(self, cli_command):

        return cli.run_cli_command(self, cli_command)
    
    def set_debug_level(self, *levels):

        return support.set_debug_level(self, *levels)
    
    def get_support_report(self):

        return support.get_support_report(self)
    
    def files(self):
        
        return files.FileBrowser(self)
    
    def _api(self):
        
        return uri.api(self)
    
    def _files(self):
        
        return uri.files(self)
        
    def _baseurl(self):
            
        return NetworkHost.baseurl(self)