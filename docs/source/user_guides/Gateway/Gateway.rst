*******
Gateway
*******

.. contents:: Table of Contents

Instantiate a Gateway object
----------------------------

.. autoclass:: cterasdk.object.Gateway.Gateway
   :special-members: __init__
   :noindex:

.. code-block:: python

   filer = Gateway('10.100.102.4') # will use HTTP over port 80

   filer = Gateway('10.100.102.4', 8080) # will use HTTP over port 8080

   filer = Gateway('vGateway-0dbc', 443, True) # will use HTTPS over port 443

.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.http['ssl'] = 'Trust'``

Logging in
==========

.. automethod:: cterasdk.object.Gateway.Gateway.test
   :noindex:

.. code-block:: python

   filer.test()

.. automethod:: cterasdk.object.Gateway.Gateway.login
   :noindex:

.. code-block:: python

   filer.login('admin', 'G3neralZ0d!')

.. automethod:: cterasdk.object.Gateway.Gateway.logout
   :noindex:

.. code-block:: python

   filer.logout()

.. automethod:: cterasdk.object.Gateway.Gateway.whoami
   :noindex:

.. code-block:: python

   filer.whoami()

Core Methods
============

.. automethod:: cterasdk.object.Gateway.Gateway.show
   :noindex:

.. code:: python

   filer.show('/status/storage/volumes')

.. automethod:: cterasdk.object.Gateway.Gateway.show_multi
   :noindex:

.. code:: python

   filer.show_multi(['/config/storage/volumes', '/status/storage/volumes'])

.. automethod:: cterasdk.object.Gateway.Gateway.get
   :noindex:

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

.. automethod:: cterasdk.object.Gateway.Gateway.get_multi
   :noindex:

.. code:: python

   """Retrieve '/config/cloudsync' and '/proc/cloudsync' at once"""

   device = filer.get_multi(['/config/cloudsync', '/proc/cloudsync'])

   print(device.config.cloudsync.cloudExtender.operationMode)
   print(device.proc.cloudsync.serviceStatus.uploadingFiles)

.. automethod:: cterasdk.object.Gateway.Gateway.put
   :noindex:

.. code:: python

   """Disable the first time wizard"""

   filer.put('/config/gui/openFirstTimeWizard', False)

   """Turn off FTP access on all shares"""

   shares = filer.get('/config/fileservices/share')

   for share in shares:

       share.exportToFTP = False

       filer.put('/config/fileservices/share/' + share.name, share)

.. automethod:: cterasdk.object.Gateway.Gateway.execute
   :noindex:

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

.. automethod:: cterasdk.object.Gateway.Gateway.add
   :noindex:

.. code:: python

   """Add a user account"""

   user = Object()

   user.username = 'mickey'

   user.fullName = 'Mickey Mouse'

   user.email = 'm.mouse@disney.com'

   user.uid = 1940

   user.password = 'M!niM0us3'

   filer.add('/config/auth/users', user)

.. automethod:: cterasdk.object.Gateway.Gateway.delete
   :noindex:

.. code:: python

   """Delete a user account"""

   user = 'mickey'

   filer.delete('/config/auth/users/' + user)

Device Configuration
====================
.. automethod:: cterasdk.edge.config.Config.get_hostname
   :noindex:

.. code-block:: python

   hostname = filer.config.hostname()

.. automethod:: cterasdk.edge.config.Config.set_hostname
   :noindex:

.. code-block:: python

   filer.config.set_hostname('Chopin')

.. automethod:: cterasdk.edge.config.Config.get_location
   :noindex:

.. code-block:: python

   location = filer.config.location()

.. automethod:: cterasdk.edge.config.Config.set_location
   :noindex:

.. code-block:: python

   filer.config.set_location('Jupiter')

.. automethod:: cterasdk.edge.config.Config.disable_wizard
   :noindex:

.. code-block:: python

   filer.config.disable_wizard()

Storage
=======

Format
^^^^^^

.. automethod:: cterasdk.edge.drive.Drive.format
   :noindex:

.. code-block:: python

   filer.drive.format('SATA1')

.. automethod:: cterasdk.edge.drive.Drive.format_all
   :noindex:

.. code-block:: python

   filer.drive.format_all()

Volumes
^^^^^^^

.. automethod:: cterasdk.edge.volumes.Volumes.add
   :noindex:

.. code-block:: python

   filer.volumes.add('localcache')

.. automethod:: cterasdk.edge.volumes.Volumes.delete
   :noindex:

.. code-block:: python

   filer.volumes.delete('localcache')

.. automethod:: cterasdk.edge.volumes.Volumes.delete_all
   :noindex:

.. code-block:: python

   filer.volumes.delete_all()

Shares
======

.. automethod:: cterasdk.edge.shares.Shares.add
   :noindex:

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

   everyone = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.LG, 'Everyone', gateway_enum.FileAccessMode.RO)
   local_admin = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.LU, 'admin', gateway_enum.FileAccessMode.RW)
   domain_admins = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.DG, 'CTERA\Domain Admins', gateway_enum.FileAccessMode.RO)
   bruce_wayne = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.DU, 'bruce.wayne@ctera.com', gateway_enum.FileAccessMode.RW)

   filer.shared.add('Accounting', 'cloud/users/Service Account/Accounting', acl = [ \
       everyone, local_admin, domain_admins, bruce_wayne \
   ])

   """Create an 'Only Authenticated Users' cloud share called 'FTP' and enable FTP access to everyone"""

   everyone = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.LG, 'Everyone', gateway_enum.FileAccessMode.RW)

   filer.shared.add('FTP', 'cloud/users/Service Account/FTP', acl = [everyone], export_to_ftp = True)

.. automethod:: cterasdk.edge.shares.Shares.add_acl
   :noindex:

.. code-block:: python

   """Add two access control entries to the 'Accounting' share"""

   domain_group = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.DG, 'CTERA\leadership', gateway_enum.FileAccessMode.RW)
   domain_user = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.DU, 'clark.kent@ctera.com', gateway_enum.FileAccessMode.RO)

   filer.shares.add_acl('Accounting', [domain_group, domain_user])

.. automethod:: cterasdk.edge.shares.Shares.set_acl
   :noindex:

.. code-block:: python

   """Set the access control entries of the 'Accounting' share"""

   domain_group = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.DG, 'CTERA\leadership', gateway_enum.FileAccessMode.RW)
   domain_user = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.DU, 'clark.kent@ctera.com', gateway_enum.FileAccessMode.RO)

   filer.shares.set_acl('Accounting', [domain_group, domain_user])

.. automethod:: cterasdk.edge.shares.Shares.remove_acl
   :noindex:

.. code-block:: python

   """Remove access control entries from the 'Accounting' share"""

   domain_group = gateway_types.RemoveShareAccessControlEntry(gateway_enum.PrincipalType.DG, 'CTERA\leadership')
   domain_user = gateway_types.RemoveShareAccessControlEntry(gateway_enum.PrincipalType.DU, 'clark.kent@ctera.com')

   filer.shares.remove_acl('Accounting', [domain_group, domain_user])

.. automethod:: cterasdk.edge.shares.Shares.set_share_winacls
   :noindex:

.. code-block:: python

   filer.shares.set_share_winacls('cloud')

.. automethod:: cterasdk.edge.shares.Shares.block_files
   :noindex:

.. code-block:: python

   filer.shares.block_files('Accounting', ['exe', 'cmd', 'bat'])

.. automethod:: cterasdk.edge.shares.Shares.modify
   :noindex:

.. code-block:: python

   """ Disable all file-access protocols on all shares """
   shares = filer.shares.get() # obtain a list of all shares

   for share in shares:
      filer.share.modify(
         share.name,
         export_to_afp=False,       # Apple File Sharing
         export_to_ftp=False,       # FTP
         export_to_nfs=False,       # NFS
         export_to_pc_agent=False,  # CTERA Agent
         export_to_rsync=False,     # rsync
         indexed=False              # Search
      )

.. automethod:: cterasdk.edge.shares.Shares.delete
   :noindex:

.. code-block:: python

   filer.shares.delete('Accounting')

Users
=====

.. automethod:: cterasdk.edge.users.Users.add
   :noindex:

.. code-block:: python

   filer.users.add('Clark', 'Kryptonite1!') # without a full name, email or custom uid

   filer.users.add('alice', 'W!z4rd0fOz!', 'Alice Wonderland') # including a full name

   filer.users.add('Bruce', 'GothamCity1!', 'Bruce Wayne', 'bruce.wayne@we.com', uid = 1940) # all

.. automethod:: cterasdk.edge.users.Users.delete
   :noindex:

.. code-block:: python

   filer.users.delete('alice')

.. automethod:: cterasdk.edge.users.Users.add_first_user
   :noindex:

.. code-block:: python

   filer.users.add_first_user('admin', 'L3tsG3tR34dyT0Rumbl3!')

Groups
======

.. automethod:: cterasdk.edge.groups.Groups.add_members
   :noindex:

.. code-block:: python

   """Add Bruce Wayne to the local Administrators group"""

   filer.groups.add_members('Administrators', [('DU', 'bruce.wayne@we.com')])

   """Add Bruce Wayne and Domain Admins to the local Administrators group"""

   filer.groups.add_members('Administrators', [('DU', 'bruce.wayne@we.com'), ('DG', 'WE\Domain Admins')])

.. automethod:: cterasdk.edge.groups.Groups.remove_members
   :noindex:

.. code-block:: python

   """Remove Bruce Wayne from the local Administrators group"""

   filer.groups.remove_members('Administrators', [('DU', 'bruce.wayne@we.com')])

   """Remove Bruce Wayne and Domain Admins from the local Administrators group"""

   filer.groups.remove_members('Administrators', [('DU', 'bruce.wayne@we.com'), ('DG', 'WE\Domain Admins')])

Active Directory
================

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.connect
   :noindex:

.. code-block:: python

   filer.directoryservice.connect('ctera.local', 'administrator', 'B4tMob!l3')

   """Connect to the EMEA Organizational Unit"""

   filer.directoryservice.connect('ctera.local', 'administrator', 'B4tMob!l3', 'ou=EMEA, dc=ctera, dc=local')

.. note:: the `ou` parameter must specify the distinguished name of the organizational unit

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.advanced_mapping
   :noindex:

.. code-block:: python

   filer.directoryservice.advanced_mapping('CTERA', 200001, 5000001)

.. note:: to retrieve a list of domain flat names, use :py:func:`Gateway.domains()`

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.disconnect
   :noindex:

.. code-block:: python

   filer.directoryservice.disconnect()

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.domains
   :noindex:

.. code-block:: python

   domains = filer.directoryservice.domains()

   print(domains)

Cloud Services
==============

.. automethod:: cterasdk.edge.services.Services.connect
   :noindex:

.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.connect['ssl'] = 'Trust'``
..

.. code-block:: python

   filer.services.connect('chopin.ctera.com', 'svc_account', 'Th3AmazingR4ce!', 'EV32') # activate as an EV32

..

.. code-block:: python

   filer.services.connect('52.204.15.122', 'svc_account', 'Th3AmazingR4ce!', 'EV64') # activate as an EV64

..

.. automethod:: cterasdk.edge.services.Services.activate
   :noindex:

   This method's behavior is identical to :py:func:`Gateway.connect()`

.. code-block:: python

   filer.services.activate('chopin.ctera.com', 'svc_account', 'fd3a-301b-88d5-e1a9-cbdb') # activate as an EV16

.. automethod:: cterasdk.edge.services.Services.reconnect
   :noindex:

.. code-block:: python

   filer.services.reconnect()

.. automethod:: cterasdk.edge.services.Services.disconnect
   :noindex:

.. code-block:: python

   filer.services.disconnect()

.. automethod:: cterasdk.edge.services.Services.enable_sso
   :noindex:

Applying a License
==================
.. automethod:: cterasdk.edge.licenses.Licenses.apply
   :noindex:

.. code-block:: python

   filer.license.apply('EV32')

.. note:: you can specify a license upon connecting the Gateway to CTERA Portal. See :py:func:`Gateway.connect()`

Caching
=======
.. automethod:: cterasdk.edge.cache.Cache.enable
   :noindex:

.. code-block:: python

   filer.cache.enable()

.. automethod:: cterasdk.edge.cache.Cache.disable
   :noindex:

.. code-block:: python

   filer.cache.disable()

.. warning:: all data synchronized from the cloud will be deleted and all unsynchronized changes will be lost.

.. automethod:: cterasdk.edge.cache.Cache.force_eviction
   :noindex:

.. code-block:: python

   filer.cache.force_eviction()

.. automethod:: cterasdk.edge.cache.Cache.pin
   :noindex:

.. code-block:: python

   """ Pin a cloud folder named 'data' owned by 'Service Account' """
   filer.cache.pin('users/Service Account/data')

.. automethod:: cterasdk.edge.cache.Cache.pin_exclude
   :noindex:

.. code-block:: python

   """ Exclude a subfolder from a pinned cloud folder """
   filer.cache.pin_exclude('users/Service Account/data/accounting')

.. automethod:: cterasdk.edge.cache.Cache.remove_pin
   :noindex:

.. code-block:: python

   """ Remove a pin from a previously pinned folder """
   filer.cache.remove_pin('users/Service Account/data')

.. automethod:: cterasdk.edge.cache.Cache.pin_all
   :noindex:

.. code-block:: python

   """ Pin all folders """
   filer.cache.pin_all()

.. automethod:: cterasdk.edge.cache.Cache.unpin_all
   :noindex:

.. code-block:: python

   """ Remove all folder pins """
   filer.cache.unpin_all()

Cloud Backup
============

.. automethod:: cterasdk.edge.backup.Backup.configure
   :noindex:

.. code-block:: python

   """Configure backup without a passphrase"""

   filer.backup.configure()

.. automethod:: cterasdk.edge.backup.Backup.start
   :noindex:

.. code-block:: python

   filer.backup.start()

.. automethod:: cterasdk.edge.backup.Backup.suspend
   :noindex:

.. code-block:: python

   filer.backup.suspend()

.. automethod:: cterasdk.edge.backup.Backup.unsuspend
   :noindex:

.. code-block:: python

   filer.backup.unsuspend()

Cloud Sync
==========
.. automethod:: cterasdk.edge.sync.Sync.suspend
   :noindex:

.. code-block:: python

   filer.sync.suspend()

.. automethod:: cterasdk.edge.sync.Sync.unsuspend
   :noindex:

.. code-block:: python

   filer.sync.unsuspend()

.. automethod:: cterasdk.edge.sync.Sync.refresh
   :noindex:

.. code-block:: python

   filer.sync.refresh()

File Access Protocols
=====================
.. automethod:: cterasdk.edge.ftp.FTP.disable
   :noindex:

.. code-block:: python

   filer.ftp.disable()

.. automethod:: cterasdk.edge.afp.AFP.disable
   :noindex:

.. code-block:: python

   filer.afp.disable()

.. automethod:: cterasdk.edge.nfs.NFS.disable
   :noindex:

.. code-block:: python

   filer.nfs.disable()

.. automethod:: cterasdk.edge.rsync.RSync.disable
   :noindex:

.. code-block:: python

   filer.rsync.disable()

Windows File Sharing (CIFS/SMB)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.smb.SMB.enable
   :noindex:

.. code-block:: python

   filer.smb.enable()

.. automethod:: cterasdk.edge.smb.SMB.disable
   :noindex:

.. code-block:: python

   filer.smb.disable()

.. automethod:: cterasdk.edge.smb.SMB.set_packet_signing
   :noindex:

.. code-block:: python

   filer.smb.set_packet_signing('If client agrees')

.. automethod:: cterasdk.edge.smb.SMB.enable_abe
   :noindex:

.. code-block:: python

   filer.smb.enable_abe()

.. automethod:: cterasdk.edge.smb.SMB.disable_abe
   :noindex:

.. code-block:: python

   filer.smb.disable_abe()

.. automethod:: cterasdk.edge.aio.AIO.enable
   :noindex:

.. code-block:: python

   filer.aio.enable()

.. automethod:: cterasdk.edge.aio.AIO.disable
   :noindex:

.. code-block:: python

   filer.aio.disable()


Network
=======
.. automethod:: cterasdk.edge.network.Network.set_static_ipaddr
   :noindex:

.. code-block:: python

   filer.network.set_static_ipaddr('10.100.102.4', '255.255.255.0', '10.100.102.1', '10.100.102.1')

   filer.show('/status/network/ports/0/ip') # will print the IP configuration

.. automethod:: cterasdk.edge.network.Network.set_static_nameserver
   :noindex:

.. code-block:: python

   filer.network.set_static_nameserver('10.100.102.1') # to set the primary name server

   filer.network.set_static_nameserver('10.100.102.1', '10.100.102.254') # to set both primary and secondary

.. automethod:: cterasdk.edge.network.Network.enable_dhcp
   :noindex:

.. code-block:: python

   filer.network.enable_dhcp()

Network Diagnostics
^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.network.Network.tcp_connect
   :noindex:

.. code-block:: python

   filer.network.tcp_connect('chopin.ctera.com', 995) # CTTP

   filer.network.tcp_connect('dc.ctera.com', 389) # LDAP

Mail Server
===========

.. automethod:: cterasdk.edge.mail.Mail.enable
   :noindex:

.. code-block:: python

   filer.mail.enable('smtp.ctera.com') # default settings

   filer.mail.enable('smtp.ctera.com', 465) # custom port number

   """Use default port number, use authentication and require TLS"""

   filer.mail.enable('smtp.ctera.com', username = 'user', password = 'secret', useTLS = True)

.. automethod:: cterasdk.edge.mail.Mail.disable
   :noindex:

.. code-block:: python

   filer.mail.disable()

Logging
=======

.. automethod:: cterasdk.edge.syslog.Syslog.enable
   :noindex:

.. code-block:: python

   filer.syslog.enable('syslog.ctera.com') # default settings

   filer.syslog.enable('syslog.ctera.com', proto = 'TCP') # use TCP

   filer.syslog.enable('syslog.ctera.com', 614, minSeverity = 'error') # use 614 UDP, severity >= error

.. automethod:: cterasdk.edge.syslog.Syslog.disable
   :noindex:

.. code-block:: python

   filer.syslog.disable()

SMB Audit Logs
^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.audit.Audit.enable
   :noindex:

.. code-block:: python

   filer.audit.enable('/logs')

.. automethod:: cterasdk.edge.audit.Audit.disable
   :noindex:

.. code-block:: python

   filer.audit.disable()

Reset
=====
.. automethod:: cterasdk.edge.power.Power.reset
   :noindex:

.. code-block:: python

   filer.power.reset() # will reset and immediately return

   filer.power.reset(True) # will reset and wait for the Gateway to boot

.. seealso:: create the first admin account after resetting the Gateway to its default settings: :py:func:`cterasdk.edge.users.Users.add_first_user()`

SSL
================

.. automethod:: cterasdk.edge.ssl.SSL.disable_http
   :noindex:

.. code-block:: python

   filer.ssl.disable_http()

.. automethod:: cterasdk.edge.ssl.SSL.enable_http
   :noindex:

.. code-block:: python

   filer.ssl.enable_http()

.. automethod:: cterasdk.edge.ssl.SSL.is_http_disabled
   :noindex:

.. code-block:: python

   filer.ssl.is_http_disabled()

.. automethod:: cterasdk.edge.ssl.SSL.is_http_enabled
   :noindex:

.. code-block:: python

   filer.ssl.is_http_enabled()

.. automethod:: cterasdk.edge.ssl.SSL.upload_cert
   :noindex:

.. code-block:: python

   """
   certificate = '/home/alice/certs/certificate.crt'
   private_key = '/home/alice/certs/private.key'
   """

   filer.ssl.upload_cert(certificate, private_key)

.. danger: Proceed with caution. The integrity of the PEM encoded certificate and private key is not validated. Supplying an invalid certificate or private key may disable all administrative access to the system and would require to engage with CTERA Support professionals to re-enable access. Test your code and certificates before implementing this in production.

Power Management
================

.. automethod:: cterasdk.edge.power.Power.reboot
   :noindex:

.. code-block:: python

   filer.power.reboot() # will reboot and immediately return

   filer.power.reboot(True) # will reboot and wait

.. automethod:: cterasdk.edge.power.Power.shutdown
   :noindex:

.. code-block:: python

   filer.power.shutdown()

Support
=======

Support Report
^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.support.Support.get_support_report
   :noindex:

Debug
^^^^^

.. automethod:: cterasdk.edge.support.Support.set_debug_level
   :noindex:

.. code-block:: python

   filer.support.set_debug_level('backup', 'process', 'cttp', 'samba')

   filer.support.set_debug_level('info')

   filer.support.set_debug_level('caching', 'evictor')

Telnet Access
^^^^^^^^^^^^^
.. automethod:: cterasdk.edge.telnet.Telnet.enable
   :noindex:

.. code-block:: python

   filer.telnet.enable('a7df639a')

.. automethod:: cterasdk.edge.telnet.Telnet.disable
   :noindex:

.. code-block:: python

   filer.telnet.disable()
