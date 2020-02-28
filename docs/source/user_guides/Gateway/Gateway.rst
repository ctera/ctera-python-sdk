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

.. autofunction:: cterasdk.object.Gateway.Gateway.test
   :noindex:

.. code-block:: python

   filer.test()

.. autofunction:: cterasdk.object.Gateway.Gateway.login
   :noindex:

.. code-block:: python

   filer.login('admin', 'G3neralZ0d!')

.. autofunction:: cterasdk.object.Gateway.Gateway.logout
   :noindex:

.. code-block:: python

   filer.logout()

.. autofunction:: cterasdk.object.Gateway.Gateway.whoami
   :noindex:

.. code-block:: python

   filer.whoami()

Core Methods
============

.. autofunction:: cterasdk.object.Gateway.Gateway.show
   :noindex:

.. code:: python

   filer.show('/status/storage/volumes')

.. autofunction:: cterasdk.object.Gateway.Gateway.show_multi
   :noindex:

.. code:: python

   filer.show_multi(['/config/storage/volumes', '/status/storage/volumes'])

.. autofunction:: cterasdk.object.Gateway.Gateway.get
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

.. autofunction:: cterasdk.object.Gateway.Gateway.get_multi
   :noindex:

.. code:: python

   """Retrieve '/config/cloudsync' and '/proc/cloudsync' at once"""

   device = filer.get_multi(['/config/cloudsync', '/proc/cloudsync'])

   print(device.config.cloudsync.cloudExtender.operationMode)
   print(device.proc.cloudsync.serviceStatus.uploadingFiles)

.. autofunction:: cterasdk.object.Gateway.Gateway.put
   :noindex:

.. code:: python

   """Disable the first time wizard"""

   filer.put('/config/gui/openFirstTimeWizard', False)

   """Turn off FTP access on all shares"""

   shares = filer.get('/config/fileservices/share')

   for share in shares:

       share.exportToFTP = False

       filer.put('/config/fileservices/share/' + share.name, share)

.. autofunction:: cterasdk.object.Gateway.Gateway.execute
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

.. autofunction:: cterasdk.object.Gateway.Gateway.add
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

.. autofunction:: cterasdk.object.Gateway.Gateway.delete
   :noindex:

.. code:: python

   """Delete a user account"""

   user = 'mickey'

   filer.delete('/config/auth/users/' + user)

Device Configuration
====================
.. autofunction:: cterasdk.edge.config.Config.get_hostname
   :noindex:

.. code-block:: python

   hostname = filer.config.hostname()

.. autofunction:: cterasdk.edge.config.Config.set_hostname
   :noindex:

.. code-block:: python

   filer.config.set_hostname('Chopin')

.. autofunction:: cterasdk.edge.config.Config.get_location
   :noindex:

.. code-block:: python

   location = filer.config.location()

.. autofunction:: cterasdk.edge.config.Config.set_location
   :noindex:

.. code-block:: python

   filer.config.set_location('Jupiter')

Storage
=======

Format
^^^^^^

.. autofunction:: cterasdk.edge.drive.Drive.format
   :noindex:

.. code-block:: python

   filer.drive.format('SATA1')

.. autofunction:: cterasdk.edge.drive.Drive.format_all
   :noindex:

.. code-block:: python

   filer.drive.format_all()

Volumes
^^^^^^^

.. autofunction:: cterasdk.edge.volumes.Volumes.add
   :noindex:

.. code-block:: python

   filer.volumes.add('localcache')

.. autofunction:: cterasdk.edge.volumes.Volumes.delete
   :noindex:

.. code-block:: python

   filer.volumes.delete('localcache')

.. autofunction:: cterasdk.edge.volumes.Volumes.delete_all
   :noindex:

.. code-block:: python

   filer.volumes.delete_all()

Shares
======

.. autofunction:: cterasdk.edge.shares.Shares.add
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

   filer.shared.add('Accounting', 'cloud/users/Service Account/Accounting', acl = [ \
       ('LG', 'Everyone', 'RO'), \
       ('LU', 'admin', 'RW'), \
       ('DG', 'CTERA\Domain Admins', 'RO'), \
       ('DU', 'bruce.wayne@ctera.com', 'RW') \
   ])

   """Create an 'Only Authenticated Users' cloud share called 'FTP' and enable FTP access to everyone"""

   filer.shared.add('FTP', 'cloud/users/Service Account/FTP', acl = [ \
       ('LG', 'Everyone', 'RW')
   ], exportToFTP = True)

.. autofunction:: cterasdk.edge.shares.Shares.add_acl
   :noindex:

.. code-block:: python

   """Add two access control entries to the 'Accounting' share"""

   filer.shares.add_acl('Accounting', [ \
       ('DG', 'CTERA\leadership', 'RW'), \
       ('DU', 'clark.kent@ctera.com', 'RO') \
   ])

.. autofunction:: cterasdk.edge.shares.Shares.set_acl
   :noindex:

.. code-block:: python

   """Set two access control entries to the 'Accounting' share"""

   filer.shares.set_acl('Accounting', [ \
       ('DG', 'CTERA\leadership', 'RW'), \
       ('DU', 'clark.kent@ctera.com', 'RO') \
   ])

.. autofunction:: cterasdk.edge.shares.Shares.remove_acl
   :noindex:

.. code-block:: python

   """Remove two access control entries from the 'Accounting' share"""

   filer.shares.remove_acl('Accounting', [ ('DG', 'CTERA\leadership'), ('DU', 'clark.kent@ctera.com') ])

.. autofunction:: cterasdk.edge.shares.Shares.delete
   :noindex:

.. code-block:: python

   filer.shares.delete('Accounting')

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

.. autofunction:: cterasdk.edge.users.Users.add
   :noindex:

.. code-block:: python

   filer.users.add('Clark', 'Kryptonite1!') # without a full name, email or custom uid

   filer.users.add('alice', 'W!z4rd0fOz!', 'Alice Wonderland') # including a full name

   filer.users.add('Bruce', 'GothamCity1!', 'Bruce Wayne', 'bruce.wayne@we.com', uid = 1940) # all

.. autofunction:: cterasdk.edge.users.Users.delete
   :noindex:

.. code-block:: python

   filer.users.delete('alice')

.. autofunction:: cterasdk.edge.users.Users.add_first_user
   :noindex:

.. code-block:: python

   filer.users.add_first_user('admin', 'L3tsG3tR34dyT0Rumbl3!')

Groups
======

.. autofunction:: cterasdk.edge.groups.Groups.add_members
   :noindex:

.. code-block:: python

   """Add Bruce Wayne to the local Administrators group"""

   filer.groups.add_members('Administrators', [('DU', 'bruce.wayne@we.com')])

   """Add Bruce Wayne and Domain Admins to the local Administrators group"""

   filer.groups.add_members('Administrators', [('DU', 'bruce.wayne@we.com'), ('DG', 'WE\Domain Admins')])

.. autofunction:: cterasdk.edge.groups.Groups.remove_members
   :noindex:

.. code-block:: python

   """Remove Bruce Wayne from the local Administrators group"""

   filer.groups.remove_members('Administrators', [('DU', 'bruce.wayne@we.com')])

   """Remove Bruce Wayne and Domain Admins from the local Administrators group"""

   filer.groups.remove_members('Administrators', [('DU', 'bruce.wayne@we.com'), ('DG', 'WE\Domain Admins')])

Active Directory
================

.. autofunction:: cterasdk.edge.directoryservice.DirectoryService.connect
   :noindex:

.. code-block:: python

   filer.directoryservice.connect('ctera.local', 'administrator', 'B4tMob!l3')

   """Connect to the EMEA Organizational Unit"""

   filer.directoryservice.connect('ctera.local', 'administrator', 'B4tMob!l3', 'ou=EMEA, dc=ctera, dc=local')

.. note:: the `ou` parameter must specify the distinguished name of the organizational unit

.. autofunction:: cterasdk.edge.directoryservice.DirectoryService.advanced_mapping
   :noindex:

.. code-block:: python

   filer.directoryservice.advanced_mapping('CTERA', 200001, 5000001)

.. note:: to retrieve a list of domain flat names, use :py:func:`Gateway.domains()`

.. autofunction:: cterasdk.edge.directoryservice.DirectoryService.disconnect
   :noindex:

.. code-block:: python

   filer.directoryservice.disconnect()

.. autofunction:: cterasdk.edge.directoryservice.DirectoryService.domains
   :noindex:

.. code-block:: python

   domains = filer.directoryservice.domains()

   print(domains)

Cloud Services
==============

.. autofunction:: cterasdk.edge.services.Services.connect
   :noindex:

.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.connect['ssl'] = 'Trust'``
..

.. code-block:: python

   filer.servics.connect('chopin.ctera.com', 'svc_account', 'Th3AmazingR4ce!', 'EV32') # activate as an EV32

..

.. code-block:: python

   filer.servics.connect('52.204.15.122', 'svc_account', 'Th3AmazingR4ce!', 'EV64') # activate as an EV64

..

.. autofunction:: cterasdk.edge.services.Services.activate
   :noindex:

   This method's behavior is identical to :py:func:`Gateway.connect()`

.. code-block:: python

   filer.services.activate('chopin.ctera.com', 'svc_account', 'fd3a-301b-88d5-e1a9-cbdb') # activate as an EV16

.. autofunction:: cterasdk.edge.services.Services.reconnect
   :noindex:

.. code-block:: python

   filer.services.reconnect()

.. autofunction:: cterasdk.edge.services.Services.disconnect
   :noindex:

.. code-block:: python

   filer.services.disconnect()

.. autofunction:: cterasdk.edge.services.Services.enable_sso
   :noindex:

Applying a License
==================
.. autofunction:: cterasdk.edge.licenses.Licenses.apply
   :noindex:

.. code-block:: python

   filer.license.apply('EV32')

.. note:: you can specify a license upon connecting the Gateway to CTERA Portal. See :py:func:`Gateway.connect()`

Caching
=======
.. autofunction:: cterasdk.edge.cache.Cache.enable
   :noindex:

.. code-block:: python

   filer.cache.enable()

.. autofunction:: cterasdk.edge.cache.Cache.disable
   :noindex:

.. code-block:: python

   filer.cache.disable()

.. warning:: all data synchronized from the cloud will be deleted and all unsynchronized changes will be lost.

.. autofunction:: cterasdk.edge.cache.Cache.force_eviction
   :noindex:

.. code-block:: python

   filer.cache.force_eviction()

Cloud Backup
============

.. autofunction:: cterasdk.edge.backup.Backup.configure
   :noindex:

.. code-block:: python

   """Configure backup without a passphrase"""

   filer.backup.configure()

.. autofunction:: cterasdk.edge.backup.Backup.start
   :noindex:

.. code-block:: python

   filer.backup.start()

.. autofunction:: cterasdk.edge.backup.Backup.suspend
   :noindex:

.. code-block:: python

   filer.backup.suspend()

.. autofunction:: cterasdk.edge.backup.Backup.unsuspend
   :noindex:

.. code-block:: python

   filer.backup.unsuspend()

Cloud Sync
==========
.. autofunction:: cterasdk.edge.sync.Sync.suspend
   :noindex:

.. code-block:: python

   filer.sync.suspend()

.. autofunction:: cterasdk.edge.sync.Sync.unsuspend
   :noindex:

.. code-block:: python

   filer.sync.unsuspend()

.. autofunction:: cterasdk.edge.sync.Sync.refresh
   :noindex:

.. code-block:: python

   filer.sync.refresh()

File Access Protocols
=====================
.. autofunction:: cterasdk.edge.ftp.FTP.disable
   :noindex:

.. code-block:: python

   filer.ftp.disable()

.. autofunction:: cterasdk.edge.afp.AFP.disable
   :noindex:

.. code-block:: python

   filer.afp.disable()

.. autofunction:: cterasdk.edge.nfs.NFS.disable
   :noindex:

.. code-block:: python

   filer.nfs.disable()

.. autofunction:: cterasdk.edge.rsync.RSync.disable
   :noindex:

.. code-block:: python

   filer.rsync.disable()

Windows File Sharing (CIFS/SMB)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: cterasdk.edge.smb.SMB.enable
   :noindex:

.. code-block:: python

   filer.smb.enable()

.. autofunction:: cterasdk.edge.smb.SMB.disable
   :noindex:

.. code-block:: python

   filer.smb.disable()

.. autofunction:: cterasdk.edge.smb.SMB.set_packet_signing
   :noindex:

.. code-block:: python

   filer.smb.set_packet_signing('If client agrees')

.. autofunction:: cterasdk.edge.smb.SMB.enable_abe
   :noindex:

.. code-block:: python

   filer.smb.enable_abe()

.. autofunction:: cterasdk.edge.smb.SMB.disable_abe
   :noindex:

.. code-block:: python

   filer.smb.disable_abe()

.. autofunction:: cterasdk.edge.aio.AIO.enable
   :noindex:

.. code-block:: python

   filer.aio.enable()

.. autofunction:: cterasdk.edge.aio.AIO.disable
   :noindex:

.. code-block:: python

   filer.aio.disable()


Network
=======
.. autofunction:: cterasdk.edge.network.Network.set_static_ipaddr
   :noindex:

.. code-block:: python

   filer.network.set_static_ipaddr('10.100.102.4', '255.255.255.0', '10.100.102.1', '10.100.102.1')

   filer.show('/status/network/ports/0/ip') # will print the IP configuration

.. autofunction:: cterasdk.edge.network.Network.set_static_nameserver
   :noindex:

.. code-block:: python

   filer.network.set_static_nameserver('10.100.102.1') # to set the primary name server

   filer.network.set_static_nameserver('10.100.102.1', '10.100.102.254') # to set both primary and secondary

.. autofunction:: cterasdk.edge.network.Network.enable_dhcp
   :noindex:

.. code-block:: python

   filer.network.enable_dhcp()

Network Diagnostics
^^^^^^^^^^^^^^^^^^^

.. autofunction:: cterasdk.edge.network.Network.tcp_connect
   :noindex:

.. code-block:: python

   filer.network.tcp_connect('chopin.ctera.com', 995) # CTTP

   filer.network.tcp_connect('dc.ctera.com', 389) # LDAP

Mail Server
===========

.. autofunction:: cterasdk.edge.mail.Mail.enable
   :noindex:

.. code-block:: python

   filer.mail.enable('smtp.ctera.com') # default settings

   filer.mail.enable('smtp.ctera.com', 465) # custom port number

   """Use default port number, use authentication and require TLS"""

   filer.mail.enable('smtp.ctera.com', username = 'user', password = 'secret', useTLS = True)

.. autofunction:: cterasdk.edge.mail.Mail.disable
   :noindex:

.. code-block:: python

   filer.mail.disable()

Logging
=======

.. autofunction:: cterasdk.edge.syslog.Syslog.enable
   :noindex:

.. code-block:: python

   filer.syslog.enable('syslog.ctera.com') # default settings

   filer.syslog.enable('syslog.ctera.com', proto = 'TCP') # use TCP

   filer.syslog.enable('syslog.ctera.com', 614, minSeverity = 'error') # use 614 UDP, severity >= error

.. autofunction:: cterasdk.edge.syslog.Syslog.disable
   :noindex:

.. code-block:: python

   filer.syslog.disable()

SMB Audit Logs
^^^^^^^^^^^^^^

.. autofunction:: cterasdk.edge.audit.Audit.enable
   :noindex:

.. code-block:: python

   filer.audit.enable('/logs')

.. autofunction:: cterasdk.edge.audit.Audit.disable
   :noindex:

.. code-block:: python

   filer.audit.disable()

Reset
=====
.. autofunction:: cterasdk.edge.power.Power.reset
   :noindex:

.. code-block:: python

   filer.power.reset() # will reset and immediately return

   filer.power.reset(True) # will reset and wait for the Gateway to boot

.. seealso:: create the first admin account after resetting the Gateway to its default settings: :py:func:`cterasdk.edge.users.Users.add_first_user()`

Power Management
================

.. autofunction:: cterasdk.edge.power.Power.reboot
   :noindex:

.. code-block:: python

   filer.power.reboot() # will reboot and immediately return

   filer.power.reboot(True) # will reboot and wait

.. autofunction:: cterasdk.edge.power.Power.shutdown
   :noindex:

.. code-block:: python

   filer.power.shutdown()

Support
=======

Support Report
^^^^^^^^^^^^^^

.. autofunction:: cterasdk.edge.support.Support.get_support_report
   :noindex:

Debug
^^^^^

.. autofunction:: cterasdk.edge.support.Support.set_debug_level
   :noindex:

.. code-block:: python

   filer.support.set_debug_level('backup', 'process', 'cttp', 'samba')

   filer.support.set_debug_level('info')

   filer.support.set_debug_level('caching', 'evictor')

Telnet Access
^^^^^^^^^^^^^
.. autofunction:: cterasdk.edge.telnet.Telnet.enable
   :noindex:

.. code-block:: python

   filer.telnet.enable('a7df639a')

.. autofunction:: cterasdk.edge.telnet.Telnet.disable
   :noindex:

.. code-block:: python

   filer.telnet.disable()
