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

.. seealso:: Execute the file-eviction process: :py:func:`cterasdk.edge.cache.Cache.force_eviction()`, Reboot the Gateway: :py:func:`cterasdk.edge.power.reboot()`, Execute tcp connect: :py:func:`Gateway.tcp_connect()`

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

.. automethod:: cterasdk.edge.config.Config.export
   :noindex:

.. code-block:: python

   filer.config.export()

.. automethod:: cterasdk.edge.config.Config.import_config
   :noindex:

.. code-block:: python

   """Import Edge Filer configuration from file"""
   filer.config.import_config(r'C:\Users\bwayne\Downloads\EdgeFiler.xml')

   """Import configuration without network settings"""
   filer.config.import_config(r'C:\Users\bwayne\Downloads\EdgeFiler.xml', exclude=[
       '/config/network'
   ])

   """Import configuration without the 'logs' and 'public' shares"""
   filer.config.import_config(r'C:\Users\bwayne\Downloads\EdgeFiler.xml', exclude=[
       '/config/fileservices/share/logs',
       '/config/fileservices/share/public'
   ])

Code Snippets
=============

.. code-block:: python

   filer.get('/status/device/runningFirmware')  # Get firmware version

   """Get the entire device status object"""
   status = filer.get('/status/device')
   print(status.runningFirmware, status.MacAddress)

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


Local Deduplication
^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.dedup.Dedup.enable
   :noindex:

.. code-block:: python

   """Enable local de-duplication without rebooting the Edge Filer"""
   filer.dedup.enable()

   """Enable local de-duplication and wait for reboot to complete"""
   filer.dedup.enable(reboot=True, wait=True)

.. automethod:: cterasdk.edge.dedup.Dedup.disable
   :noindex:

.. code-block:: python

   """Disable local de-duplication without rebooting the Edge Filer"""
   filer.dedup.disable()

   """Disable local de-duplication and wait for reboot to complete"""
   filer.dedup.disable(reboot=True, wait=True)


.. automethod:: cterasdk.edge.dedup.Dedup.status
   :noindex:

.. code-block:: python

   print(filer.dedup.status())

.. automethod:: cterasdk.edge.dedup.Regeneration.run
   :noindex:

.. code-block:: python

   filer.dedup.regen.run()

.. automethod:: cterasdk.edge.dedup.Regeneration.status
   :noindex:

.. code-block:: python

   print(filer.dedup.regen.status())


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

   filer.shares.add('Accounting', 'cloud/users/Service Account/Accounting', acl = [ \
       everyone, local_admin, domain_admins, bruce_wayne \
   ])

   """Create an 'Only Authenticated Users' cloud share called 'FTP' and enable FTP access to everyone"""

   everyone = gateway_types.ShareAccessControlEntry(gateway_enum.PrincipalType.LG, 'Everyone', gateway_enum.FileAccessMode.RW)

   filer.shares.add('FTP', 'cloud/users/Service Account/FTP', acl = [everyone], export_to_ftp = True)

   """Add an NFS share and enable access to two hosts"""
   nfs_client_1 = gateway_types.NFSv3AccessControlEntry('192.168.0.1', '255.255.255.0', gateway_enum.FileAccessMode.RW)  # read write
   nfs_client_2 = gateway_types.NFSv3AccessControlEntry('192.168.0.2', '255.255.255.0', gateway_enum.FileAccessMode.RO)  # read only
   filer.shares.add('NFS', 'cloud/users/Service Account/NFS', export_to_nfs=True, trusted_nfs_clients=[nfs_client_1, nfs_client_2])


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

.. automethod:: cterasdk.edge.users.Users.modify
   :noindex:

.. code-block:: python

   filer.users.modify('Clark', 'Passw0rd1!') # Change a user's password
   filer.users.modify('Clark', email='clark.kent@krypton.com') # Change a user's email

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
   member = gateway_types.UserGroupEntry(gateway_enum.PrincipalType.DU, 'bruce.wayne@we.com')
   filer.groups.add_members('Administrators', [member])

   """Add Bruce Wayne and Domain Admins to the local Administrators group"""

   domain_user = gateway_types.UserGroupEntry(gateway_enum.PrincipalType.DU, 'bruce.wayne@we.com')
   domain_group = gateway_types.UserGroupEntry(gateway_enum.PrincipalType.DG, 'WE\Domain Admins')
   filer.groups.add_members('Administrators', [domain_user, domain_group])

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

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.get_advanced_mapping
   :noindex:

.. code-block:: python

   for domain, mapping in filer.directoryservice.get_advanced_mapping().items():
       print(domain)
       print(mapping)

.. note:: to retrieve a list of domain flat names, use :py:func:`cterasdk.edge.directoryservice.domains()`

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.set_advanced_mapping
   :noindex:

.. code-block:: python

   """Create a list of domain mappings"""

   advanced_mapping = [
       common_types.ADDomainIDMapping('CTERA-PRD', 1000001, 2000000),
       common_types.ADDomainIDMapping('CTERA-LAB', 2000001, 3000000),
       common_types.ADDomainIDMapping('CTERA-LDR', 3000001, 4000000)
   ]

   filer.directoryservice.set_advanced_mapping(advanced_mapping)  # this function will skip domains that are not found

.. note:: to retrieve a list of domain flat names, use :py:func:`cterasdk.edge.directoryservice.domains()`

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.disconnect
   :noindex:

.. code-block:: python

   filer.directoryservice.disconnect()

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.domains
   :noindex:

.. code-block:: python

   domains = filer.directoryservice.domains()

   print(domains)

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.set_static_domain_controller
   :noindex:

.. code-block:: python

   filer.directoryservice.set_static_domain_controller('192.168.90.1')

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.get_static_domain_controller
   :noindex:

.. code-block:: python

   domain_controller = filer.directoryservice.get_static_domain_controller()
   print(domain_controller)

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.remove_static_domain_controller
   :noindex:

.. code-block:: python

   filer.directoryservice.remove_static_domain_controller()

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

   This method's behavior is identical to :py:func:`cterasdk.edge.services.Services.connect()`

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

.. note:: you can specify a license upon connecting the Gateway to CTERA Portal. See :py:func:`cterasdk.edge.services.Services.connect()`

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

Cloud Backup Files
^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.backup.BackupFiles.unselect_all
   :noindex:

.. code-block:: python

   filer.backup.files.unselect_all()

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

.. automethod:: cterasdk.edge.sync.Sync.exclude_files
   :noindex:

.. code-block:: python

   filer.sync.exclude_files(['exe', 'cmd', 'bat'])  # exclude file extensions

   filer.sync.exclude_files(filenames=['Cloud Sync.lnk', 'The quick brown fox.docx'])  # exclude file names

   """Exclude file extensions and file names"""
   filer.sync.exclude_files(['exe', 'cmd'], ['Cloud Sync.lnk'])

   """
   Create a custom exclusion rule

   Exclude files that their name starts with 'tmp' and smaller than 1 MB (1,048,576 bytes)
   """
   name_filter_rule = common_types.FileFilterBuilder.name().startswith('tmp')
   size_filter_rule = common_types.FileFilterBuilder.size().less_than(1048576)
   exclusion_rule = common_types.FilterBackupSet('Custom exclusion rule', filter_rules=[name_filter_rule, size_filter_rule])

   filer.sync.exclude_files(custom_exclusion_rules=[exclusion_rule])

.. automethod:: cterasdk.edge.sync.Sync.remove_file_exclusion_rules
    :noindex:

.. code-block:: python

   filer.sync.remove_file_exclusion_rules()

.. automethod:: cterasdk.edge.sync.Sync.evict
   :noindex:

.. code-block:: python

   """Evict a directory"""
   background_task_ref = filer.sync.evict('/Share/path/to/sub/directory')  # non-blocking call
   print(background_task_ref)

   """Evict a directory and wait for eviction to complete - blocking"""
   filer.sync.evict('/Share/path/to/sub/directory', wait=True)  # blocking call


Cloud Sync Bandwidth Throttling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.sync.CloudSyncBandwidthThrottling.get_policy
   :noindex:

.. automethod:: cterasdk.edge.sync.CloudSyncBandwidthThrottling.set_policy
   :noindex:

.. code-block:: python

   """Throttle bandwidth during business hours on week days: Monday - Friday"""
   schedule1 = common_types.TimeRange().start('07:00:00').end('19:00:00').days(common_enum.DayOfWeek.Weekdays).build()
   rule1 = common_types.ThrottlingRuleBuilder().upload(50).download(50).schedule(schedule1).build()

   """Throttle bandwidth off business hours on week days: Monday - Friday"""
   schedule2 = common_types.TimeRange().start('19:00:00').end('07:00:00').days(common_enum.DayOfWeek.Weekdays).build()
   rule2 = common_types.ThrottlingRuleBuilder().upload(100).download(100).schedule(schedule2).build()

   """Throttle bandwidth during weekends: Saturday, Sunday"""
   schedule3 = common_types.TimeRange().start('00:00:00').end('23:59:00').days(common_enum.DayOfWeek.Weekend).build()
   rule3 = common_types.ThrottlingRuleBuilder().upload(500).download(500).schedule(schedule3).build()

   filer.sync.throttling.set_policy([rule1, rule2, rule3])


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

.. automethod:: cterasdk.edge.network.Network.set_mtu
   :noindex:

.. code-block:: python

   filer.network.set_mtu(1320)  # set the maximum transmission unit (MTU) to 1320

   filer.network.set_mtu(9000)  # configure 'jumbo' frames (MTU: 9000)

.. automethod:: cterasdk.edge.network.Network.reset_mtu
   :noindex:

.. code-block:: python

   filer.network.reset_mtu()  # disable custom mtu configuration and restore default setting (1500)

.. automethod:: cterasdk.edge.network.Network.get_static_routes
   :noindex:

.. code-block:: python

   # get static routes
   filer.network.get_static_routes()

.. automethod:: cterasdk.edge.network.Network.add_static_route
   :noindex:

.. code-block:: python

   # add static route from 10.10.12.1 to 192.168.55.7/32
   filer.network.add_static_route('10.10.12.1', '192.168.55.7/32')

   # add static route from 10.100.102.4 to 172.18.100.0/24
   filer.network.add_static_route('10.100.102.4', '172.18.100.0/24')

.. automethod:: cterasdk.edge.network.Network.remove_static_route
   :noindex:

.. code-block:: python

   # remove static route 192.168.55.7/32
   filer.network.remove_static_route('192.168.55.7/32')

.. automethod:: cterasdk.edge.network.Network.clean_all_static_routes
   :noindex:

.. code-block:: python

   # remove all static routes -  (clean)
   filer.network.clean_all_static_routes()


Network Diagnostics
^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.network.Network.tcp_connect
   :noindex:

.. code-block:: python

   cttp_service = gateway_types.TCPService('chopin.ctera.com', 995)
   result = filer.network.tcp_connect(cttp_service)
   if result.is_open:
       print('Success')
       # do something...
   else:
       print('Failure')

   ldap_service = gateway_types.TCPService('dc.ctera.com', 389)
   filer.network.tcp_connect(ldap_service)

.. automethod:: cterasdk.edge.network.Network.diagnose
   :noindex:

.. code-block:: python

   services = []
   services.append(gateway_types.TCPService('192.168.90.1', 389))  # LDAP
   services.append(gateway_types.TCPService('ctera.portal.com', 995))  # CTTP
   services.append(gateway_types.TCPService('ctera.portal.com', 443))  # HTTPS
   result = filer.network.diagnose(services)
   for result in results:
       print(result.host, result.port, result.is_open)


.. automethod:: cterasdk.edge.network.Network.iperf
   :noindex:

.. code-block:: python

   filer.network.iperf('192.168.1.145')  # iperf server: 192.168.1.145, threads: 1, measure upload over TCP port 5201

   filer.network.iperf('192.168.1.145', port=85201, threads=5)  # Customized port and number of threads

   filer.network.iperf('192.168.1.145', direction=gateway_enum.Traffic.Download)  # Measure download speed

   filer.network.iperf('192.168.1.145', protocol=gateway_enum.IPProtocol.UDP)  # Use UDP

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

.. automethod:: cterasdk.edge.logs.Logs.settings
   :noindex:

.. automethod:: cterasdk.edge.logs.Logs.logs
   :noindex:

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

.. code-block:: python

   """
   ca_certificate = './certs/certificate.crt'
   """

   filer.ssl.set_trusted_ca(ca_certificate)

.. automethod:: cterasdk.edge.ssl.SSL.get_storage_ca
   :noindex:

.. automethod:: cterasdk.edge.ssl.SSL.remove_storage_ca
   :noindex:

.. automethod:: cterasdk.edge.ssl.SSL.import_certificate
   :noindex:

.. code-block:: python

   """
   certificate = './certs/certificate.crt'
   intermediate_cert = './certs/certificate1.crt'
   ca_certificate = './certs/certificate2.crt'
   private_key = './certs/private.key'
   """

   """
   Specify certificates in the following order: domain cert, intermediary certs, CA cert
   You may include as many intermediate certificates as needed
   """
   filer.ssl.import_certificate(private_key, certificate, intermediate_cert, ca_certificate)

.. danger: Exercise caution. Test thoroughly prior to implementing in production. Ensure the integrity of the PEM encoded private key and certificates. Supplying an invalid private key or certificate will disable administrative access to the filer and would require CTERA Support to re-enable it.

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

SNMP
====

.. automethod:: cterasdk.edge.snmp.SNMP.is_enabled
   :noindex:

.. code-block:: python

   filer.snmp.is_enabled()

.. automethod:: cterasdk.edge.snmp.SNMP.enable
   :noindex:

.. code-block:: python

   filer.snmp.enable(community_str='MpPcKl2sArSdTLZ4URj4')  # enable SNMP v2c
   filer.snmp.enable(username='snmp_user', auth_password='gVQBaHSOGV', privacy_password='VG0zbn5aJ')  # enable SNMP v3

.. automethod:: cterasdk.edge.snmp.SNMP.disable
   :noindex:

   filer.snmp.disable()

.. automethod:: cterasdk.edge.snmp.SNMP.modify
   :noindex:

   filer.snmp.modify(community_str='L0K2zGpgmOQH2CXaUSuB', username='snmp_user', auth_password='gVQBaHSOGV', privacy_password='VG0zbn5aJ')

.. automethod:: cterasdk.edge.snmp.SNMP.get_configuration
   :noindex:

   filer.snmp.get_configuration()

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


SSH Access
^^^^^^^^^^
.. automethod:: cterasdk.edge.ssh.SSH.enable
   :noindex:

.. code-block:: python

   """Enable SSH access"""
   filer.ssh.enable()

   """Enable SSH access using a public key file"""
   filer.ssh.enable(public_key_file='./public_key.pub')  # relative to the current directory
   filer.ssh.enable(public_key_file='C:\\Users\\jsmith\\Desktop\\public_key.pub')  # full path

   """Generate an RSA key pair and enable SSH access"""

   from cryptography.hazmat.primitives.asymmetric import rsa
   from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

   private_key = rsa.generate_private_key(public_exponent=exponent, key_size=key_size)
   public_key = private_key.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH).decode('utf-8')

   filer.ssh.enable(public_key)

   """Print PEM-encoded RSA private key"""
   print(private_key.private_bytes(Encoding.PEM, PrivateFormat.OpenSSH, NoEncryption()).decode('utf-8'))

   """Print OpenSSH formatted RSA public key"""
   print(public_key)

.. automethod:: cterasdk.edge.ssh.SSH.disable
   :noindex:

.. code-block:: python

   filer.ssh.disable()


CTERA Migrate
=============

.. automethod:: cterasdk.edge.migration_tool.MigrationTool.list_shares
   :noindex:

.. code-block:: python

   """ List all shares available on a source host """
   credentials = gateway_types.HostCredentials('source-hostname', 'username', 'password')
   filer.mtool.list_shares(credentials)

   """ List all shares available on the current Edge Filer """
   credentials = gateway_types.HostCredentials.localhost()
   filer.mtool.list_shares(credentials)

.. automethod:: cterasdk.edge.migration_tool.MigrationTool.list_tasks
   :noindex:

.. code-block:: python

   """ Print all tasks, optional flag to list deleted tasks """
   for task in filer.mtool.list_tasks(deleted=False):
       print(task)

.. automethod:: cterasdk.edge.migration_tool.MigrationTool.start
   :noindex:

.. code-block:: python

   filer.mtool.start(task)

.. automethod:: cterasdk.edge.migration_tool.MigrationTool.stop
   :noindex:

.. code-block:: python

   filer.mtool.stop(task)

.. automethod:: cterasdk.edge.migration_tool.MigrationTool.delete
   :noindex:

.. code-block:: python

   filer.mtool.delete(filer.mtool.list_tasks())  # delete all tasks

.. automethod:: cterasdk.edge.migration_tool.MigrationTool.restore
   :noindex:

.. code-block:: python

   filer.mtool.restore(filer.mtool.list_tasks(deleted=True))  # recover all deleted tasks

.. automethod:: cterasdk.edge.migration_tool.MigrationTool.details
   :noindex:

.. code-block:: python

   filer.mtool.details(task)

.. automethod:: cterasdk.edge.migration_tool.MigrationTool.results
   :noindex:

.. code-block:: python

   filer.mtool.results(task)


Discovery Tasks
^^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.migration_tool.Discovery.list_tasks
   :noindex:

.. code-block:: python

   """ Print all discovery tasks, optional flag to list deleted tasks """
   for task in filer.mtool.discovery.list_tasks(deleted=False):
       print(task)

.. automethod:: cterasdk.edge.migration_tool.Discovery.add
   :noindex:

.. code-block:: python

   credentials = gateway_types.HostCredentials('source-hostname', 'username', 'password')
   task = filer.mtool.discovery.add('my-discovery', credentials, ['share1', 'share2'], auto_start=False, log_every_file=True, notes='job 1')


   """Add a local discovery task"""
   credentials = gateway_types.HostCredentials.localhost()
   task = filer.mtool.discovery.add('my-discovery', credentials, ['share1', 'share2'], log_every_file=True, notes='local discovery job')

   """Run the task"""
   filer.mtool.start(task)

.. automethod:: cterasdk.edge.migration_tool.Discovery.update
   :noindex:


Migration Tasks
^^^^^^^^^^^^^^^

.. automethod:: cterasdk.edge.migration_tool.Migration.list_tasks
   :noindex:

.. code-block:: python

   """ Print all migration tasks, optional flag to list deleted tasks """
   for task in filer.mtool.migration.list_tasks(deleted=False):
       print(task)

.. automethod:: cterasdk.edge.migration_tool.Migration.add
   :noindex:

.. code-block:: python

   credentials = gateway_types.HostCredentials('source-hostname', 'username', 'password')
   task = filer.mtool.migration.add('my-discovery', credentials, ['share1', 'share2'], auto_start=False, winacls=True, cloud_folder='my_cloud_folder', create_cloud_folder_per_share=False, compute_checksum=False, exclude=['*.pdf', '*.jpg'], include=['*.png', '*.avi'], notes='migration job 1')

   """Run the task"""
   filer.mtool.start(task)
