*******
Gateway
*******

.. contents:: Table of Contents

Instantiate a Gateway object
----------------------------

.. py:class:: Gateway(host[, port = 80][, https = False])

   :param host: The fully qualified domain name, hostname or an IPv4 address of the Gateway
   :param port: Set a custom port number (0 - 65535), defaults to ``80``
   :param https: Set to ``True`` to require HTTPS, defaults to ``False``
   :type host: str
   :type port: int
   :type https: bool
   
.. code-block:: python

   filer = Gateway('10.100.102.4') # will use HTTP over port 80
   
   filer = Gateway('10.100.102.4', 8080) # will use HTTP over port 8080
   
   filer = Gateway('vGateway-0dbc', 443, True) # will use HTTPS over port 443
   
.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.http['ssl'] = 'Trust'``

Logging in
==========

.. py:method:: Gateway.test()

   Verification check to ensure the target host is a Gateway.
   
.. code-block:: python

   filer.test()
   
.. py:method:: Gateway.login(username, password)

   Login to the Gateway.

   :param username: username
   :param password: password
   :type username: str
   :type password: str
   
.. code-block:: python

   filer.login('admin', 'G3neralZ0d!')

.. py:method:: Gateway.logout()

   Logout from Gateway.
   
.. code-block:: python

   filer.logout()

.. py:method:: Gateway.whoami()

   Return the name of the logged in user.
   
   :returns: the name of the logged in user
   :rtype: str
   
.. code-block:: python

   filer.whoami()

Core Methods
============

.. py:method:: Gateway.show(path)

   Print a Gateway schema object as a JSON string.
   
.. code:: python
   
   filer.show('/status/storage/volumes')

.. py:method:: Gateway.show_multi(paths)

   Print one or more Gateway schema objects as a JSON string.
   
.. code:: python
   
   filer.show_multi(['/config/storage/volumes', '/status/storage/volumes'])

.. py:method:: Gateway.get(path)

   Retrieve a Gateway schema object as a Python object.
   
.. code:: python

   """Retrieve the device configuration and print it as JSON string"""
   
   config = filer.get('/config')
   print(config)
   
   """Retrieve the device settings and print the hostname and location settings"""
   
   settings = filer.get('/config/device')
   
   print(settings.hostname)
   print(settings.location)
   
   """Retrieve a list of volumes and print the name of the first volume"""
   
   volumes  = filer.get('/status/storage/volumes') # returns a list of volumes 
   
   print(volumes[0].name) # will print the name of the first volume
   
   """Retrieve the network settings and print the MTU setting"""
   
   network  = filer.get('/config/network') # returns network settings
   
   print(network.ports[0].ethernet.mtu) # will print the MTU setting

.. py:method:: Gateway.get_multi(paths)

   Retrieve one or more Gateway schema objects as a Python object.
   
.. code:: python

   """Retrieve '/config/cloudsync' and '/proc/cloudsync' at once"""

   device = filer.get_multi(['/config/cloudsync', '/proc/cloudsync'])
   
   print(device.config.cloudsync.cloudExtender.operationMode)
   print(device.proc.cloudsync.serviceStatus.uploadingFiles)

.. py:method:: Gateway.put(path, value)

   Update a Gateway schema object or attribute.
   
.. code:: python

   """Disable the first time wizard"""
   
   filer.put('/config/gui/openFirstTimeWizard', False)
   
   """Turn off FTP access on all shares"""
   
   shares = filer.get('/config/fileservices/share')
   
   for share in shares:
       
       share.exportToFTP = False
       
       filer.put('/config/fileservices/share/' + share.name, share)

.. py:method:: Gateway.execute(path, name[, param = None])

   Execute a Gateway schema object method.
   
.. code:: python

   """Execute the file-eviction process"""

   filer.execute('/config/cloudsync', 'forceExecuteEvictor') # doesn't require a param

   """Reboot the Gateway"""
   
   filer.execute('/statuc/device', 'reboot') # doesn't require a param
   
   """TCP Connect"""
   
   param = Object()
   
   param.address = 'chopin.ctera.com'
   
   param.port = 995 # CTTP
   
   bgTask = filer.execute('/status/network', 'tcpconnect', param)
   
   print(bgTask)
   
.. seealso:: Execute the file-eviction process: :py:func:`Gateway.force_eviction()`, Reboot the Gateway: :py:func:`Gateway.reboot()`, Execute tcp connect: :py:func:`Gateway.tcp_connect()`

.. py:method:: Gateway.add(path, param)

   Add a Gateway schema object.
   
.. code:: python

   """Add a user account"""

   user = Object()
   
   user.username = 'mickey'
   
   user.fullName = 'Mickey Mouse'
   
   user.email = 'm.mouse@disney.com'
   
   user.uid = 1940
   
   user.password = 'M!niM0us3'
   
   filer.add('/config/auth/users', user)

.. py:method:: Gateway.delete(path)

   Delete a Gateway schema object.
   
.. code:: python

   """Delete a user account"""

   user = 'mickey'

   filer.delete('/config/auth/users/' + user)
   
Device Configuration
====================

.. py:method:: Gateway.hostname()

   Retrieve the Gateway's hostname.
   
   :returns: hostname
   :rtype: str
   
.. code-block:: python
   
   hostname = filer.hostname()

.. py:method:: Gateway.set_hostname(hostname)

   Set the Gateway's hostname.
   
   :param hostname: hostname
   :type hostname: str
   
.. code-block:: python
   
   filer.set_hostname('Chopin')
   
.. py:method:: Gateway.location()

   Retrieve the Gateway's physical location attribute.
   
   :returns: location
   :rtype: str
   
.. code-block:: python
   
   location = filer.location()

.. py:method:: Gateway.set_location(location)

   Set the Gateway's location.
   
   :param hostname: location
   :type location: str

.. code-block:: python

   filer.set_location('Jupiter')
   
Storage
=======

Format
^^^^^^

.. py:method:: Gateway.format_drive(name)

   Format a drive.
   
   :param name: the drive name
   :type name: str
   
.. code-block:: python

   filer.format_drive('SATA1')

.. py:method:: Gateway.format_all_drives()

   Format all drives.
   
.. code-block:: python

   filer.format_all_drives()
   
Volumes
^^^^^^^

.. py:method:: Gateway.add_volume(name[, size = None][, fileSystemType = 'xfs'][, device = None][, passphrase = None])

   Add a volume.
   
   :param name: the volume name
   :param size: size in GB
   :param device: drive or array name
   :param passphrase: passphrase encryption

.. code-block:: python

   filer.add_volume('localcache')

.. py:method:: Gateway.delete_volume(name)

   Delete a volume.
   
   :param name: the volume name
   
.. code-block:: python

   filer.delete_volume('localcache')

.. py:method:: Gateway.delete_all_volumes()

   Delete all volumes.
   
.. code-block:: python

   filer.delete_all_volumes()

Shares
======

.. py:method:: Gateway.add_share(name, directory[, acl = []][, access = 'winAclMode'][, csc = 'manual'][, comment = None][, exportToAFP = False][, exportToFTP = False][, exportToNFS = False][, exportToPCAgent = False][, exportToRSync = False])

   Add a network share.
   
   :param name: the share name
   :param directory: full directory path
   :param acl: a list of 3-tuple access control entries
   :param access: the Windows File Sharing authentication mode, defaults to ``winAclMode``
   :param csc: the client side caching (offline files) configuration, defaults to ``manual``
   :param comment: comment
   :param exportToAFP: whether to enable AFP access, defaults to ``False``
   :param exportToFTP: whether to enable FTP access, defaults to ``False``
   :param exportToNFS: whether to enable NFS access, defaults to ``False``
   :param exportToPCAgent: whether to allow as a destination share for CTERA Backup Agents, defaults to ``False``
   :param exportToRSync: whether to enable access over rsync, defaults to ``False``
   :type name: str
   :type directory: str
   :type acl: list[tuple(str, str, str)]
   :type access: str
   :type csc: str
   :type comment: str
   :type exportToAFP: bool
   :type exportToFTP: bool
   :type exportToNFS: bool
   :type exportToPCAgent: bool
   :type exportToRSync: bool
   
.. code-block:: python

   """
   Create an ACL-enabled cloud share called 'Accounting' and define four access control entries:
   
   1) Everyone - Read Only (Local Group)
   2) admin - Read Write (Local User)
   3) Domain Admins - Read Only (Domain Group)
   4) bruce.wayne@ctera.com - Read Write (Domain User)
   
   Principal Type:
   - LG: Local Group
   - LU: Local User
   - DG: Domain Group
   - DU: Domain User
   
   Access:
   - RW: Read Write
   - RO: Read Only
   - NA: No Access
   """

   filer.add_share('Accounting', 'cloud/users/Service Account/Accounting', acl = [ \
       ('LG', 'Everyone', 'RO'), \
       ('LU', 'admin', 'RW'), \
       ('DG', 'CTERA\Domain Admins', 'RO'), \
       ('DU', 'bruce.wayne@ctera.com', 'RW') \
   ])
   
   """Create an 'Only Authenticated Users' cloud share called 'FTP' and enable FTP access to everyone"""
   
   filer.add_share('FTP', 'cloud/users/Service Account/FTP', acl = [ \
       ('LG', 'Everyone', 'RW')
   ], exportToFTP = True)

.. py:method:: Gateway.add_share_acl(name, acl)

   Add one or more access control entries to an existing share.
   
   :param name: the share name
   :param acl: a list of 3-tuple access control entries
   :type name: str
   :type acl: list[tuple(str, str, str)]
   
.. code-block:: python

   """Add two access control entries to the 'Accounting' share"""

   filer.add_share_acl('Accounting', [ \
       ('DG', 'CTERA\leadership', 'RW'), \
       ('DU', 'clark.kent@ctera.com', 'RO') \
   ])

.. py:method:: Gateway.remove_share_acl(name, acl)

   Remove one or more access control entries from an existing share.
   
   :param name: the share name
   :param acl: a list of 2-tuple access control entries
   :type name: str
   :type acl: list[tuple(str, str)]
   
.. code-block:: python

   """Remove two access control entries from the 'Accounting' share"""

   filer.remove_share_acl('Accounting', [ ('DG', 'CTERA\leadership'), ('DU', 'clark.kent@ctera.com') ])

.. py:method:: Gateway.delete_share(name)

   Delete a share.
   
.. code-block:: python

   filer.delete_share('Accounting')
   
Code Snippets
^^^^^^^^^^^^^

Disable all file-access protocols on all shares

.. code-block:: python

   shares = filer.get('/config/fileservices/share') # obtain a list of all shares

   for share in shares:

       share.exportToAFP = False            # Apple File Sharing

       share.exportToFTP = False            # FTP
       
       share.exportToNFS = False            # NFS

       share.exportToRSync = False          # rsync

       share.exportToPCAgent = False        # CTERA Agent

       share.indexed = False                # Search

       filer.put('/config/fileservices/share/' + share.name, share) # apply changes

Users
=====

.. py:method:: Gateway.add_user(username, password[, fullName = None][, email = None][, uid = None])

   Add a local user account.
   
   :param username: username
   :param password: password
   :param fullName: first and last name
   :param email: email address
   :param uid: custom uid
   :type username: str
   :type password: str
   :type fullName: str
   :type email: str
   :type uid: int

.. code-block:: python

   filer.add_user('Clark', 'Kryptonite1!') # without a full name, email or custom uid

   filer.add_user('alice', 'W!z4rd0fOz!', 'Alice Wonderland') # including a full name
   
   filer.add_user('Bruce', 'GothamCity1!', 'Bruce Wayne', 'bruce.wayne@we.com', uid = 1940) # all

.. py:method:: Gateway.delete_user(username)

   Delete a local user account.
   
   :param username: username
   :type username: str
   
.. code-block:: python

   filer.delete_user('alice')
   
.. py:method:: Gateway.add_first_user(username, password[, email])

   Add the first admin account.
   
   :param username: username
   :param password: password
   :param email: email
   :type username: str
   :type password: str
   :type email: str
   
.. code-block:: python

   filer.add_first_user('admin', 'L3tsG3tR34dyT0Rumbl3!')

..

Groups
======

.. py:method:: Gateway.add_members(group, members)

   Add one or more members to a local group.
   
   :param group: name of a local group
   :param members: a list of 2-tuple members to add
   :type group: str
   :type members: list[tuple(str, str)]

.. code-block:: python

   """Add Bruce Wayne to the local Administrators group"""
   
   filer.add_members('Administrators', [('DU', 'bruce.wayne@we.com')])
   
   """Add Bruce Wayne and Domain Admins to the local Administrators group"""
   
   filer.add_members('Administrators', [('DU', 'bruce.wayne@we.com'), ('DG', 'WE\Domain Admins')])
   
.. py:method:: Gateway.remove_members(group, members)

   Remove one or more members from a local group.
   
   :param group: name of a local group
   :param members: a list of 2-tuple members to remove
   :type group: str
   :type members: list[tuple(str, str)]

.. code-block:: python

   """Remove Bruce Wayne from the local Administrators group"""
   
   filer.remove_members('Administrators', [('DU', 'bruce.wayne@we.com')])
   
   """Remove Bruce Wayne and Domain Admins from the local Administrators group"""
   
   filer.remove_members('Administrators', [('DU', 'bruce.wayne@we.com'), ('DG', 'WE\Domain Admins')])
   
Active Directory
================

.. py:method:: Gateway.directory_services_connect(domain, username, password[, ou = None])

   Connect the Gateway to Microsoft Active Directory. 
   
   :param domain: fully qualified domain name
   :param username: username
   :param password: password
   :param ou: path to an organizational unit
   :type domain: str
   :type username: str
   :type password: str
   :type ou: str
   
   The connect method will first ensure the Gateway can establish a TCP connection over port 389 (LDAP) to `domain` using :py:func:`Gateway.tcp_connect()` prior to attempting to connect
  
.. code-block:: python

   filer.directory_services_connect('ctera.local', 'administrator', 'B4tMob!l3')
   
   """Connect to the EMEA Organizational Unit"""
   
   filer.directory_services_connect('ctera.local', 'administrator', 'B4tMob!l3', 'ou=EMEA, dc=ctera, dc=local')
   
.. note:: the `ou` parameter must specify the distinguished name of the organizational unit

.. py:method:: Gateway.advanced_mapping(domain, start, end)

   Configure advanced mapping from Windows SID's to UID/GID values.
   
   :param domain: the domain flat name
   :param start: start value
   :param end: end value
   :type domain: str
   :type start: int
   :type end: int
   
.. code-block:: python

   filer.advanced_mapping('CTERA', 200001, 5000001)
   
.. note:: to retrieve a list of domain flat names, use :py:func:`Gateway.domains()`

.. py:method:: Gateway.directory_services_disconnect()

   Disconnect from Microsoft Active Directory.
   
.. code-block:: python

   filer.directory_services_disconnect()

.. py:method:: Gateway.domains()

   List trusted Active Directory domains.
   
   :returns: a list of trusted domain flat names
   :rtype: list
   
.. code-block:: python

   domains = filer.domains()
   
   print(domains)
   
Cloud Services
==============

.. py:method:: Gateway.connect(server, user, password[, license = 'EV16'])

   Connect the Gateway to CTERA Portal.
   
   :param server: the fully qualified domain name or IPV4 address of the Portal
   :param user: username
   :param password: password
   :param license: the type of license to consume, defaults to EV16
   :type server: str
   :type user: str
   :type password: str
   :type license: str
   
   The connect method will first validate the `license` argument, ensure the Gateway can establish a TCP connection over port 995 to `server` using :py:func:`Gateway.tcp_connect()` and verify the Portal does not require device activation via code
   
.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.connect['ssl'] = 'Trust'``
..
  
.. code-block:: python

   filer.connect('chopin.ctera.com', 'svc_account', 'Th3AmazingR4ce!', 'EV32') # activate as an EV32
   
..

.. code-block:: python

   filer.connect('52.204.15.122', 'svc_account', 'Th3AmazingR4ce!', 'EV64') # activate as an EV64
   
..

.. py:method:: Gateway.activate(server, user, code[, license = 'EV16'])

   Connect the Gateway to CTERA Portal using an activation code.
   
   This method's behavior is identical to :py:func:`Gateway.connect()`
   
.. code-block:: python

   filer.activate('chopin.ctera.com', 'svc_account', 'fd3a-301b-88d5-e1a9-cbdb') # activate as an EV16

.. py:method:: Gateway.reconnect()

   Reconnect the Gateway to CTERA Portal.

.. code-block:: python

   filer.reconnect()
   
.. py:method:: Gateway.disconnect()

   Sign-out from CTERA Portal.
   
.. code-block:: python

   filer.disconnect()

.. py:method:: Gateway.enable_sso()

   Enable Single Sign-On to CTERA Portal administrators.
   
Applying a License
==================

.. py:method:: Gateway.apply_license(license)

   Apply a license.
   
   :param license: the license type
   :type license: str

.. code-block:: python

   filer.apply_license('EV32')
   
.. note:: you can specify a license upon connecting the Gateway to CTERA Portal. See :py:func:`Gateway.connect()` 
   
Caching
=======

.. py:method:: Gateway.enable_caching()

   Enable caching.
   
.. code-block:: python

   filer.enable_caching()

.. py:method:: Gateway.disable_caching()

   Disable caching.
   
.. code-block:: python

   filer.disable_caching()
   
.. warning:: all data synchronized from the cloud will be deleted and all unsynchronized changes will be lost.

.. py:method:: Gateway.force_eviction()

   Start a file-eviction process.
   
.. code-block:: python

   filer.force_eviction()
   
Cloud Backup
============

.. py:method:: Gateway.configure_backup([passphrase = None])

   Configure cloud backup.
   
   :param passphrase: a passphrase, for passphrase encrypted backups
   :type passphrase: str
   
.. code-block:: python

   """Configure backup without a passphrase"""

   filer.configure_backup()
   
.. py:method:: Gateway.start_backup()

   Start a cloud backup.
   
.. code-block:: python

   filer.start_backup()
   
.. py:method:: Gateway.suspend_backup()

   Suspend cloud backup.
   
.. code-block:: python

   filer.suspend_backup()
   
.. py:method:: Gateway.unsuspend_backup()

   Unsuspend cloud backup.
   
.. code-block:: python

   filer.unsuspend_backup()
   
Cloud Sync
==========

.. py:method:: Gateway.suspend_sync()

   Suspend cloud sync.
   
.. code-block:: python

   filer.suspend_sync()

.. py:method:: Gateway.unsuspend_sync()

   Unsuspend cloud sync.
   
.. code-block:: python

   filer.unsuspend_sync()
   
.. py:method:: Gateway.refresh_cloud_folders()

   Request an updated list of cloud folders.
   
.. code-block:: python

   filer.refresh_cloud_folders()
   
File Access Protocols
=====================

.. py:method:: Gateway.disable_ftp()

   Disable FTP.
   
.. code-block:: python

   filer.disable_ftp()

.. py:method:: Gateway.disable_afp()

   Disable AFP.
   
.. code-block:: python

   filer.disable_afp()

.. py:method:: Gateway.disable_nfs()

   Disable NFS.
   
.. code-block:: python

   filer.disable_nfs()

.. py:method:: Gateway.disable_rsync()

   Disable RSync.
   
.. code-block:: python

   filer.disable_rsync()
   
Windows File Sharing (CIFS/SMB)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: Gateway.enable_smb()

   Enable Windows file sharing (CIFS/SMB). 
   
.. code-block:: python

   filer.enable_smb()

.. py:method:: Gateway.disable_smb()

   Disable Windows File Sharing (CIFS/SMB).
   
.. code-block:: python

   filer.disable_smb()
   
.. py:method:: Gateway.set_packet_signing(mode)

   Configure SMB packet signing.
   
   :param mode: packet signing mode
   :type mode: str
   
   * Disabled
   * If client agrees
   * Required
   
.. code-block:: python

   filer.set_packet_signing('If client agrees')

.. py:method:: Gateway.enable_abe()

   Enable access based enumeration (ABE) and hide unreadable files and folders.
   
.. code-block:: python

   filer.enable_abe()

.. py:method:: Gateway.disable_abe()

   Disable access based enumeration (ABE) and show unreadable files and folders.
   
.. code-block:: python

   filer.disable_abe()
   
.. py:method:: Gateway.enable_aio()

   Enable asynchronous io.
   
.. code-block:: python

   filer.enable_aio()
   
.. py:method:: Gateway.disable_aio()

   Disable asynchronous io.
   
.. code-block:: python

   filer.disable_aio()

Network
=======

.. py:method:: Gateway.set_static_ipaddr(address, subnet, gateway, DNSServer1[, DNSServer2 = None])

   Set a static IPv4 configuration.
   
.. code-block:: python

   filer.set_static_ipaddr('10.100.102.4', '255.255.255.0', '10.100.102.1', '10.100.102.1')
   
   filer.show('/status/network/ports/0/ip') # will print the IP configuration
   
.. py:method:: Gateway.set_static_nameserver(DNSServer1[, DNSServer2 = None])

   Set a static name server.
   
.. code-block:: python

   filer.set_static_nameserver('10.100.102.1') # to set the primary name server
   
   filer.set_static_nameserver('10.100.102.1', '10.100.102.254') # to set both primary and secondary
   
.. py:method:: Gateway.enable_dhcp()

   Enable DHCP.
   
.. code-block:: python
   
   filer.enable_dhcp()
   
Network Diagnostics
^^^^^^^^^^^^^^^^^^^

.. py:method:: Gateway.tcp_connect(address, port)

   Verify a TCP connection can be established from the Gateway to a target host.
   
   :param address: fully qulified domain name, hostname or an IPv4 address
   :param port: a port number (0 - 65535)
   :type address: str
   :type port: int
   
.. code-block:: python
   
   filer.tcp_connect('chopin.ctera.com', 995) # CTTP
   
   filer.tcp_connect('dc.ctera.com', 389) # LDAP
   
Mail Server
===========

.. py:method:: Gateway.enable_mail_server(SMTPServer[, port = 25][, username = None][, password = None][, useTLS = True])

   Configure mail server to receive e-mail notifications.
   
   :param SMTPServer: fully qualified domain name, hostname or IPv4 address of the mail server
   :param port: a custom port number (0 - 65535), defaults to ``25``
   :param username: username (in case mail server requires authentication)
   :param password: password
   :param useTLS: use TLS
   :type SMTPServer: str
   :type port: int
   :type username: str
   :type password: str
   :type useTLS: bool
   
.. code-block:: python
   
   filer.enable_mail_server('smtp.ctera.com') # default settings
   
   filer.enable_mail_server('smtp.ctera.com', 465) # custom port number
   
   """Use default port number, use authentication and require TLS"""
   
   filer.enable_mail_server('smtp.ctera.com', username = 'user', password = 'secret', useTLS = True)

.. py:method:: Gateway.disable_mail_server()

   Disbable mail server.
   
.. code-block:: python
   
   filer.disable_mail_server()
   
Logging
=======

.. py:method:: Gateway.enable_syslog(server[, port = 514][, proto = IPProtocol.UDP][, minSeverity = "info"])

   Forward logs to a syslog server.
   
   :param server: fully qualified domain name, hostname or IPv4 address
   :param port: a custom port (0 - 65535), defaults to ``514``
   :param proto: the IP protocol, defaults to ``'UDP'``
   :param minSeverity: the minimum severity of logs to forward, defaults to ``'info'``
   :type server: str
   :type port: int
   :type proto: str
   :type minSeverity: str
   
.. code-block:: python
   
   filer.enable_syslog('syslog.ctera.com') # default settings
   
   filer.enable_syslog('syslog.ctera.com', proto = 'TCP') # use TCP
   
   filer.enable_syslog('syslog.ctera.com', 614, minSeverity = 'error') # use 614 UDP, severity >= error

.. py:method:: Gateway.disable_syslog()

   Disable log forwarding to a syslog server.
   
.. code-block:: python
   
   filer.disable_syslog()

SMB Audit Logs
^^^^^^^^^^^^^^

.. py:method:: Gateway.enable_audit_logs(path[, auditEvents = ['WD', 'AD', 'REA', 'DC', 'WA', 'DE', 'WDAC', 'WO']][, logKeepPeriod = 30][, maxLogKBSize = 102400][, maxRotateTime = 1440][, includeAuditLogTag = True][, humanReadableAuditLog = False])

   Enable SMB audit logs
   
   :param path: log file destination
   :param auditEvents: list of audit events, defaults to write and delete events
   :param logKeepPeriod: keep logs for (days)
   :param maxLogKBSize: rotate audit.log file 
   :param maxRotateTime: rotate audit.log file every (minutes), defaults to ``1440`` (24 hours)
   :param includeAuditLogTag: 
   :param humanReadableAuditLog: log acl changes in a human-readable format
   :type path: str
   :type auditEvents: list[str]
   :type logKeepPeriod: int
   :type maxLogKBSize: int
   :type maxRotateTime: int
   :type includeAuditLogTag: bool
   :type humanReadableAuditLog: bool
   
.. code-block:: python
   
   filer.enable_audit_logs('/logs')

.. py:method:: Gateway.disable_audit_logs()

.. code-block:: python
   
   filer.disable_audit_logs()
   
Reset
=====

.. py:method:: Gateway.reset([wait = False] )

   Reset the Gateway to its default settings.
   
   :param wait: whether to wait for the Gateway to boot, defaults to ``False``
   :type wait: bool
   
.. code-block:: python
   
   filer.reset() # will reset and immediately return
   
   filer.reset(True) # will reset and wait for the Gateway to boot
   
.. seealso:: create the first admin account after resetting the Gateway to its default settings: :py:func:`Gateway.add_first_user()` 
   
Power Management
================

.. py:method:: Gateway.reboot([wait = False])

   Reboot the Gateway.
   
   :param wait: whether to wait for the Gateway to boot, defaults to ``False``
   :type wait: bool
   
.. code-block:: python

   filer.reboot() # will reboot and immediately return

   filer.reboot(True) # will reboot and wait

.. py:method:: Gateway.shutdown()

   Turn off the Gateway.

.. code-block:: python

   filer.shutdown()
   
Support
=======

Support Report
^^^^^^^^^^^^^^

.. py:method:: Gateway.get_support_report()

   Download a support report.

Debug
^^^^^

.. py:method:: Gateway.set_debug_level(levels...)

   Set debug level.
   
   :param levels: a comma separated list of debug levels
   
.. code-block:: python

   filer.set_debug_level('backup', 'process', 'cttp', 'samba')
   
   filer.set_debug_level('info')
   
   filer.set_debug_level('caching', 'evictor')

Telnet Access
^^^^^^^^^^^^^

.. py:method:: Gateway.enable_telnet(code)

   Enable telnet access.
   
   :param code: telnet access code
   
.. code-block:: python

   filer.enable_telnet('a7df639a')

.. py:method:: Gateway.disable_telnet()

   Disable telnet access.
   
.. code-block:: python

   filer.disable_telnet()