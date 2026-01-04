========================
Configuration Management
========================

Logging In
==========

.. automethod:: cterasdk.objects.synchronous.edge.Edge.login
   :noindex:

.. code-block:: python

   edge.login('admin', 'G3neralZ0d!')

.. automethod:: cterasdk.objects.synchronous.edge.Edge.logout
   :noindex:

.. code-block:: python

   edge.logout()

Device Configuration
====================

.. automethod:: cterasdk.edge.config.Config.get_hostname
   :noindex:

.. code-block:: python

   hostname = edge.config.get_hostname()

.. automethod:: cterasdk.edge.config.Config.set_hostname
   :noindex:

.. code-block:: python

   edge.config.set_hostname('Chopin')

.. automethod:: cterasdk.edge.config.Config.get_location
   :noindex:

.. code-block:: python

   location = edge.config.get_location()

.. automethod:: cterasdk.edge.config.Config.set_location
   :noindex:

.. code-block:: python

   edge.config.set_location('Jupiter')

.. automethod:: cterasdk.edge.config.Config.disable_wizard
   :noindex:

.. code-block:: python

   edge.config.disable_wizard()

.. automethod:: cterasdk.edge.config.Config.export
   :noindex:

.. code-block:: python

   edge.config.export()

.. automethod:: cterasdk.edge.config.Config.import_config
   :noindex:

.. code-block:: python

   """Import Edge Filer configuration from file"""
   edge.config.import_config(r'C:\Users\bwayne\Downloads\EdgeFiler.xml')

   """Import configuration without network settings"""
   edge.config.import_config(r'C:\Users\bwayne\Downloads\EdgeFiler.xml', exclude=[
       '/config/network'
   ])

   """Import configuration without the 'logs' and 'public' shares"""
   edge.config.import_config(r'C:\Users\bwayne\Downloads\EdgeFiler.xml', exclude=[
       '/config/fileservices/share/logs',
       '/config/fileservices/share/public'
   ])

Storage
=======

Format Drives
-------------

.. automethod:: cterasdk.edge.drive.Drive.format
   :noindex:

.. code-block:: python

   edge.drive.format('SATA1')

.. automethod:: cterasdk.edge.drive.Drive.format_all
   :noindex:

.. code-block:: python

   edge.drive.format_all()

RAID Array
----------

.. automethod:: cterasdk.edge.array.Array.get
   :noindex:

.. code-block:: python

   """All arrays"""
   all_arrays = edge.array.get()

   """Get array by name"""
   lvm1 = edge.array.get('LVM1')

.. automethod:: cterasdk.edge.array.Array.add
   :noindex:

.. code-block:: python

   """Create a logical volume 'LVM1' using all available drives"""
   edge.array.add('LVM1', edge_enum.RAIDLevel.LVM, members=[drive.name for drive in edge.drive.get()])

.. automethod:: cterasdk.edge.array.Array.delete
   :noindex:

.. code-block:: python

   """Delete 'LVM1' array"""
   edge.array.delete('LVM1')

.. automethod:: cterasdk.edge.array.Array.delete_all
   :noindex:

.. code-block:: python

   """Delete all arrays"""
   edge.array.delete_all()


Volume Management
-----------------

.. automethod:: cterasdk.edge.volumes.Volumes.add
   :noindex:

.. code-block:: python

   edge.volumes.add('localcache')

.. automethod:: cterasdk.edge.volumes.Volumes.delete
   :noindex:

.. code-block:: python

   edge.volumes.delete('localcache')

.. automethod:: cterasdk.edge.volumes.Volumes.delete_all
   :noindex:

.. code-block:: python

   edge.volumes.delete_all()


Deduplication
-------------

.. automethod:: cterasdk.edge.dedup.Dedup.is_enabled
   :noindex:

.. code-block:: python

   """Check if deduplication is enabled"""
   edge.dedup.is_enabled()

.. automethod:: cterasdk.edge.dedup.Dedup.enable
   :noindex:

.. code-block:: python

   """Enable local de-duplication without rebooting the Edge Filer"""
   edge.dedup.enable()

   """Enable local de-duplication and wait for reboot to complete"""
   edge.dedup.enable(reboot=True, wait=True)

.. automethod:: cterasdk.edge.dedup.Dedup.disable
   :noindex:

.. code-block:: python

   """Disable local de-duplication without rebooting the Edge Filer"""
   edge.dedup.disable()

   """Disable local de-duplication and wait for reboot to complete"""
   edge.dedup.disable(reboot=True, wait=True)


.. automethod:: cterasdk.edge.dedup.Dedup.status
   :noindex:

.. code-block:: python

   print(edge.dedup.status())

.. automethod:: cterasdk.edge.dedup.Regeneration.run
   :noindex:

.. code-block:: python

   edge.dedup.regen.run()

.. automethod:: cterasdk.edge.dedup.Regeneration.status
   :noindex:

.. code-block:: python

   print(edge.dedup.regen.status())


Network Shares
==============

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

   everyone = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.LG, 'Everyone', edge_enum.FileAccessMode.RO)
   local_admin = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.LU, 'admin', edge_enum.FileAccessMode.RW)
   domain_admins = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.DG, 'CTERA\Domain Admins', edge_enum.FileAccessMode.RO)
   bruce_wayne = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.DU, 'bruce.wayne@ctera.com', edge_enum.FileAccessMode.RW)

   edge.shares.add('Accounting', 'cloud/users/Service Account/Accounting', acl = [ \
       everyone, local_admin, domain_admins, bruce_wayne \
   ])

   """Create an 'Only Authenticated Users' cloud share called 'FTP' and enable FTP access to everyone"""

   everyone = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.LG, 'Everyone', edge_enum.FileAccessMode.RW)

   edge.shares.add('FTP', 'cloud/users/Service Account/FTP', acl = [everyone], export_to_ftp = True)

   """Add an NFS share and enable access to two hosts"""
   nfs_client_1 = edge_types.NFSv3AccessControlEntry('192.168.0.1', '255.255.255.0', edge_enum.FileAccessMode.RW)  # read write
   nfs_client_2 = edge_types.NFSv3AccessControlEntry('192.168.0.2', '255.255.255.0', edge_enum.FileAccessMode.RO)  # read only
   edge.shares.add('NFS', 'cloud/users/Service Account/NFS', export_to_nfs=True, trusted_nfs_clients=[nfs_client_1, nfs_client_2])


.. automethod:: cterasdk.edge.shares.Shares.add_acl
   :noindex:

.. code-block:: python

   """Add two access control entries to the 'Accounting' share"""

   domain_group = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.DG, 'CTERA\leadership', edge_enum.FileAccessMode.RW)
   domain_user = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.DU, 'clark.kent@ctera.com', edge_enum.FileAccessMode.RO)

   edge.shares.add_acl('Accounting', [domain_group, domain_user])

.. automethod:: cterasdk.edge.shares.Shares.set_acl
   :noindex:

.. code-block:: python

   """Set the access control entries of the 'Accounting' share"""

   domain_group = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.DG, 'CTERA\leadership', edge_enum.FileAccessMode.RW)
   domain_user = edge_types.ShareAccessControlEntry(edge_enum.PrincipalType.DU, 'clark.kent@ctera.com', edge_enum.FileAccessMode.RO)

   edge.shares.set_acl('Accounting', [domain_group, domain_user])

.. automethod:: cterasdk.edge.shares.Shares.remove_acl
   :noindex:

.. code-block:: python

   """Remove access control entries from the 'Accounting' share"""

   domain_group = edge_types.RemoveShareAccessControlEntry(edge_enum.PrincipalType.DG, 'CTERA\leadership')
   domain_user = edge_types.RemoveShareAccessControlEntry(edge_enum.PrincipalType.DU, 'clark.kent@ctera.com')

   edge.shares.remove_acl('Accounting', [domain_group, domain_user])

.. automethod:: cterasdk.edge.shares.Shares.set_share_winacls
   :noindex:

.. code-block:: python

   edge.shares.set_share_winacls('cloud')

.. automethod:: cterasdk.edge.shares.Shares.block_files
   :noindex:

.. code-block:: python

   edge.shares.block_files('Accounting', ['exe', 'cmd', 'bat'])

.. automethod:: cterasdk.edge.shares.Shares.modify
   :noindex:

.. code-block:: python

   """ Disable all file-access protocols on all shares """
   shares = edge.shares.get() # obtain a list of all shares

   for share in shares:
      edge.share.modify(
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

   edge.shares.delete('Accounting')

Local Users
===========

.. automethod:: cterasdk.edge.users.Users.add
   :noindex:

.. code-block:: python

   edge.users.add('Clark', 'Kryptonite1!') # without a full name, email or custom uid

   edge.users.add('alice', 'W!z4rd0fOz!', 'Alice Wonderland') # including a full name

   edge.users.add('Bruce', 'GothamCity1!', 'Bruce Wayne', 'bruce.wayne@we.com', uid = 1940) # all

.. automethod:: cterasdk.edge.users.Users.modify
   :noindex:

.. code-block:: python

   edge.users.modify('Clark', 'Passw0rd1!') # Change a user's password
   edge.users.modify('Clark', email='clark.kent@krypton.com') # Change a user's email

.. automethod:: cterasdk.edge.users.Users.delete
   :noindex:

.. code-block:: python

   edge.users.delete('alice')

.. automethod:: cterasdk.edge.users.Users.add_first_user
   :noindex:

.. code-block:: python

   edge.users.add_first_user('admin', 'L3tsG3tR34dyT0Rumbl3!')

Local Groups
============

.. automethod:: cterasdk.edge.groups.Groups.add_members
   :noindex:

.. code-block:: python

   """Add Bruce Wayne to the local Administrators group"""
   member = edge_types.UserGroupEntry(edge_enum.PrincipalType.DU, 'bruce.wayne@we.com')
   edge.groups.add_members('Administrators', [member])

   """Add Bruce Wayne and Domain Admins to the local Administrators group"""

   domain_user = edge_types.UserGroupEntry(edge_enum.PrincipalType.DU, 'bruce.wayne@we.com')
   domain_group = edge_types.UserGroupEntry(edge_enum.PrincipalType.DG, 'WE\Domain Admins')
   edge.groups.add_members('Administrators', [domain_user, domain_group])

.. automethod:: cterasdk.edge.groups.Groups.remove_members
   :noindex:

.. code-block:: python

   """Remove Bruce Wayne from the local Administrators group"""

   edge.groups.remove_members('Administrators', [('DU', 'bruce.wayne@we.com')])

   """Remove Bruce Wayne and Domain Admins from the local Administrators group"""

   edge.groups.remove_members('Administrators', [('DU', 'bruce.wayne@we.com'), ('DG', 'WE\Domain Admins')])

Active Directory
================

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.connect
   :noindex:

.. code-block:: python

   edge.directoryservice.connect('ctera.local', 'administrator', 'B4tMob!l3')

   """Connect to the EMEA Organizational Unit"""

   edge.directoryservice.connect('ctera.local', 'administrator', 'B4tMob!l3', 'ou=EMEA, dc=ctera, dc=local')

.. note:: the `ou` parameter must specify the distinguished name of the organizational unit

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.get_advanced_mapping
   :noindex:

.. code-block:: python

   for domain, mapping in edge.directoryservice.get_advanced_mapping().items():
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

   edge.directoryservice.set_advanced_mapping(advanced_mapping)  # this function will skip domains that are not found

.. note::  This method sets the advanced mapping of domains and requires the full list of mappings.
   It does not append to the existing configuration—any existing mappings will be overwritten.
.. note:: to retrieve a list of domain flat names, use :py:func:`cterasdk.edge.directoryservice.domains()`

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.disconnect
   :noindex:

.. code-block:: python

   edge.directoryservice.disconnect()

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.domains
   :noindex:

.. code-block:: python

   domains = edge.directoryservice.domains()

   print(domains)

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.set_static_domain_controller
   :noindex:

.. code-block:: python

   edge.directoryservice.set_static_domain_controller('192.168.90.1')

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.get_static_domain_controller
   :noindex:

.. code-block:: python

   domain_controller = edge.directoryservice.get_static_domain_controller()
   print(domain_controller)

.. automethod:: cterasdk.edge.directoryservice.DirectoryService.remove_static_domain_controller
   :noindex:

.. code-block:: python

   edge.directoryservice.remove_static_domain_controller()

Connecting to CTERA Portal
==========================

.. automethod:: cterasdk.edge.services.Services.connect
   :noindex:

.. warning:: To ignore certificate errors when connecting to CTERA Portal, use: ``cterasdk.settings.edge.syn.services.ssl = False``
..

.. code-block:: python

   edge.services.connect('tenant.ctera.com', 'svc_account', 'Th3AmazingR4ce!', 'EV32') # activate as an EV32

..

.. code-block:: python

   edge.services.connect('52.204.15.122', 'svc_account', 'Th3AmazingR4ce!', 'EV64') # activate as an EV64

..

.. automethod:: cterasdk.edge.services.Services.activate
   :noindex:

   This method's behavior is identical to :py:func:`cterasdk.edge.services.Services.connect()`

.. code-block:: python

   edge.services.activate('tenant.ctera.com', 'svc_account', 'fd3a-301b-88d5-e1a9-cbdb') # activate as an EV16

.. automethod:: cterasdk.edge.services.Services.reconnect
   :noindex:

.. code-block:: python

   edge.services.reconnect()

.. automethod:: cterasdk.edge.services.Services.disconnect
   :noindex:

.. code-block:: python

   edge.services.disconnect()

.. automethod:: cterasdk.edge.services.Services.enable_sso
   :noindex:

Configuring a License
=====================

.. automethod:: cterasdk.edge.licenses.Licenses.apply
   :noindex:

.. code-block:: python

   edge.license.apply('EV32')

.. note:: A license can also be specified upon connecting the Edge Filer to the Portal. See :py:func:`cterasdk.edge.services.Services.connect()` for more details.

Cache Management
================

.. automethod:: cterasdk.edge.cache.Cache.enable
   :noindex:

.. code-block:: python

   edge.cache.enable()

.. automethod:: cterasdk.edge.cache.Cache.disable
   :noindex:

.. code-block:: python

   edge.cache.disable()

.. warning:: All data synchronized from the cloud will be deleted and all unsynchronized changes will be lost.

.. automethod:: cterasdk.edge.cache.Cache.force_eviction
   :noindex:

.. code-block:: python

   edge.cache.force_eviction()

Subfolder Pinning
-----------------

.. automethod:: cterasdk.edge.cache.Cache.pin
   :noindex:

.. code-block:: python

   """ Pin a cloud folder named 'data' owned by 'Service Account' """
   edge.cache.pin('users/Service Account/data')

.. automethod:: cterasdk.edge.cache.Cache.pin_exclude
   :noindex:

.. code-block:: python

   """ Exclude a subfolder from a pinned cloud folder """
   edge.cache.pin_exclude('users/Service Account/data/accounting')

.. automethod:: cterasdk.edge.cache.Cache.remove_pin
   :noindex:

.. code-block:: python

   """ Remove a pin from a previously pinned folder """
   edge.cache.remove_pin('users/Service Account/data')

.. automethod:: cterasdk.edge.cache.Cache.pin_all
   :noindex:

.. code-block:: python

   """ Pin all folders """
   edge.cache.pin_all()

.. automethod:: cterasdk.edge.cache.Cache.unpin_all
   :noindex:

.. code-block:: python

   """ Remove all folder pins """
   edge.cache.unpin_all()

Cloud Backup
============

.. automethod:: cterasdk.edge.backup.Backup.configure
   :noindex:

.. code-block:: python

   """Configure backup without a passphrase"""

   edge.backup.configure()

.. automethod:: cterasdk.edge.backup.Backup.start
   :noindex:

.. code-block:: python

   edge.backup.start()

.. automethod:: cterasdk.edge.backup.Backup.suspend
   :noindex:

.. code-block:: python

   edge.backup.suspend()

.. automethod:: cterasdk.edge.backup.Backup.unsuspend
   :noindex:

.. code-block:: python

   edge.backup.unsuspend()

Backup Selection
----------------

.. automethod:: cterasdk.edge.backup.BackupFiles.unselect_all
   :noindex:

.. code-block:: python

   edge.backup.files.unselect_all()

Cloud Synchronization
=====================

.. automethod:: cterasdk.edge.sync.Sync.suspend
   :noindex:

.. code-block:: python

   edge.sync.suspend()

.. automethod:: cterasdk.edge.sync.Sync.unsuspend
   :noindex:

.. code-block:: python

   edge.sync.unsuspend()

.. automethod:: cterasdk.edge.sync.Sync.exclude_files
   :noindex:

.. code-block:: python

   edge.sync.exclude_files(['exe', 'cmd', 'bat'])  # exclude file extensions

   edge.sync.exclude_files(filenames=['Cloud Sync.lnk', 'The quick brown fox.docx'])  # exclude file names

   """Exclude file extensions and file names"""
   edge.sync.exclude_files(['exe', 'cmd'], ['Cloud Sync.lnk'])

   """
   Create a custom exclusion rule

   Exclude files that their name starts with 'tmp' and smaller than 1 MB (1,048,576 bytes)
   """
   name_filter_rule = common_types.FileFilterBuilder.name().startswith('tmp')
   size_filter_rule = common_types.FileFilterBuilder.size().less_than(1048576)
   exclusion_rule = common_types.FilterBackupSet('Custom exclusion rule', filter_rules=[name_filter_rule, size_filter_rule])

   edge.sync.exclude_files(custom_exclusion_rules=[exclusion_rule])

.. automethod:: cterasdk.edge.sync.Sync.remove_file_exclusion_rules
    :noindex:

.. code-block:: python

   edge.sync.remove_file_exclusion_rules()

.. automethod:: cterasdk.edge.sync.Sync.evict
   :noindex:

.. code-block:: python

   """Evict a directory"""
   background_task_ref = edge.sync.evict('/Share/path/to/sub/directory')  # non-blocking call
   print(background_task_ref)

   """Evict a directory and wait for eviction to complete - blocking"""
   edge.sync.evict('/Share/path/to/sub/directory', wait=True)  # blocking call


Bandwidth Throttling
--------------------

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

   edge.sync.throttling.set_policy([rule1, rule2, rule3])


File Access Protocols
=====================

.. automethod:: cterasdk.edge.ftp.FTP.disable
   :noindex:

.. code-block:: python

   edge.ftp.disable()

.. automethod:: cterasdk.edge.afp.AFP.disable
   :noindex:

.. code-block:: python

   edge.afp.disable()

.. automethod:: cterasdk.edge.nfs.NFS.disable
   :noindex:

.. code-block:: python

   edge.nfs.disable()

.. automethod:: cterasdk.edge.rsync.RSync.disable
   :noindex:

.. code-block:: python

   edge.rsync.disable()

Windows File Sharing (CIFS/SMB)
-------------------------------

.. automethod:: cterasdk.edge.smb.SMB.enable
   :noindex:

.. code-block:: python

   edge.smb.enable()

.. automethod:: cterasdk.edge.smb.SMB.disable
   :noindex:

.. code-block:: python

   edge.smb.disable()

.. automethod:: cterasdk.edge.smb.SMB.set_packet_signing
   :noindex:

.. code-block:: python

   edge.smb.set_packet_signing('If client agrees')

.. automethod:: cterasdk.edge.smb.SMB.enable_abe
   :noindex:

.. code-block:: python

   edge.smb.enable_abe()

.. automethod:: cterasdk.edge.smb.SMB.disable_abe
   :noindex:

.. code-block:: python

   edge.smb.disable_abe()

.. automethod:: cterasdk.edge.aio.AIO.enable
   :noindex:

.. code-block:: python

   edge.aio.enable()

.. automethod:: cterasdk.edge.aio.AIO.disable
   :noindex:

.. code-block:: python

   edge.aio.disable()


Network
=======

Version 7.11+
-------------

.. automethod:: cterasdk.edge.network.Network.interface
   :noindex:

.. automethod:: cterasdk.edge.network.Network.port
   :noindex:

.. automethod:: cterasdk.edge.network.Network.deduce_port
   :noindex:

.. automethod:: cterasdk.edge.network.Network.status
   :noindex:

.. automethod:: cterasdk.edge.network.Network.ipconfig
   :noindex:

.. automethod:: cterasdk.edge.network.Network.set_static_ipaddr
   :noindex:

.. automethod:: cterasdk.edge.network.Network.set_static_nameserver
   :noindex:

.. automethod:: cterasdk.edge.network.Network.enable_dhcp
   :noindex:

.. automethod:: cterasdk.edge.network.MTU711.reset
   :noindex:

.. automethod:: cterasdk.edge.network.MTU711.modify
   :noindex:

.. automethod:: cterasdk.edge.network.StaticRoutes711.get
   :noindex:

.. automethod:: cterasdk.edge.network.StaticRoutes711.add
   :noindex:

.. automethod:: cterasdk.edge.network.StaticRoutes711.delete
   :noindex:

.. automethod:: cterasdk.edge.network.StaticRoutes711.clear
   :noindex:


Pre-Version 7.11
----------------

.. automethod:: cterasdk.edge.network.LegacyNetwork.set_static_ipaddr
   :noindex:

.. code-block:: python

   edge.network.set_static_ipaddr('10.100.102.4', '255.255.255.0', '10.100.102.1', '10.100.102.1')

   edge.show('/status/network/ports/0/ip') # will print the IP configuration

.. automethod:: cterasdk.edge.network.LegacyNetwork.set_static_nameserver
   :noindex:

.. code-block:: python

   edge.network.set_static_nameserver('10.100.102.1') # to set the primary name server

   edge.network.set_static_nameserver('10.100.102.1', '10.100.102.254') # to set both primary and secondary

.. automethod:: cterasdk.edge.network.LegacyNetwork.enable_dhcp
   :noindex:

.. code-block:: python

   edge.network.enable_dhcp()

.. automethod:: cterasdk.edge.network.LegacyMTU.modify
   :noindex:

.. code-block:: python

   edge.network.mtu.modify(1320)  # set the maximum transmission unit (MTU) to 1320

   edge.network.mtu.modify(9000)  # configure 'jumbo' frames (MTU: 9000)

.. automethod:: cterasdk.edge.network.LegacyMTU.reset
   :noindex:

.. code-block:: python

   edge.network.mtu.reset()  # disable custom mtu configuration and restore default setting (1500)

.. automethod:: cterasdk.edge.network.LegacyStaticRoutes.get
   :noindex:

.. code-block:: python

   edge.network.routes.get()

.. automethod:: cterasdk.edge.network.LegacyStaticRoutes.add
   :noindex:

.. code-block:: python

   edge.network.routes.add('10.10.12.1', '192.168.55.7/32')

   edge.network.routes.add('10.100.102.4', '172.18.100.0/24')

.. automethod:: cterasdk.edge.network.LegacyStaticRoutes.delete
   :noindex:

.. code-block:: python

   edge.network.routes.delete('192.168.55.7/32')

.. automethod:: cterasdk.edge.network.LegacyStaticRoutes.clear
   :noindex:

.. code-block:: python

   # remove all static routes -  (clean)
   edge.network.routes.clear()

Proxy Settings
--------------

.. automethod:: cterasdk.edge.network.Proxy.get_configuration
   :noindex:

.. code-block:: python

   configuration = edge.network.proxy.get_configuration()
   print(configuration)

.. automethod:: cterasdk.edge.network.Proxy.is_enabled
   :noindex:

.. code-block:: python

   if edge.network.proxy.is_enabled():
       print('Proxy Server is Enabled')

.. automethod:: cterasdk.edge.network.Proxy.modify
   :noindex:

.. code-block:: python

   edge.network.proxy.modify('192.168.11.11', 8081, 'proxy-user', 'proxy-user-password')

.. automethod:: cterasdk.edge.network.Proxy.disable
   :noindex:

.. code-block:: python

   edge.network.proxy.disable()

Hosts
-----

.. automethod:: cterasdk.edge.network.Hosts.get
   :noindex:

.. code-block:: python

   edge.network.hosts.get() # get a list of hosts file entries

.. automethod:: cterasdk.edge.network.Hosts.add
   :noindex:

.. code-block:: python

   edge.network.hosts.add('192.168.28.153', 'tenant.ctera.com')

.. automethod:: cterasdk.edge.network.Hosts.delete
   :noindex:

.. code-block:: python

   edge.network.hosts.delete('tenant.ctera.com')


Diagnostics
-----------

.. automethod:: cterasdk.edge.network.Diagnostics.tcp_connect
   :noindex:

.. code-block:: python

   cttp_service = edge_types.TCPService('tenant.ctera.com', 995)
   result = edge.network.diag.tcp_connect(cttp_service)
   if result.is_open:
       print('Success')
       # do something...
   else:
       print('Failure')

   ldap_service = edge_types.TCPService('dc.ctera.com', 389)
   edge.network.diag.tcp_connect(ldap_service)

.. automethod:: cterasdk.edge.network.Diagnostics.diagnose
   :noindex:

.. code-block:: python

   services = []
   services.append(edge_types.TCPService('192.168.90.1', 389))  # LDAP
   services.append(edge_types.TCPService('ctera.portal.com', 995))  # CTTP
   services.append(edge_types.TCPService('ctera.portal.com', 443))  # HTTPS
   result = edge.network.diag.diagnose(services)
   for result in results:
       print(result.host, result.port, result.is_open)


.. automethod:: cterasdk.edge.network.Diagnostics.iperf
   :noindex:

.. code-block:: python

   edge.network.diag.iperf('192.168.1.145')  # iperf server: 192.168.1.145, threads: 1, measure upload over TCP port 5201

   edge.network.diag.iperf('192.168.1.145', port=85201, threads=5)  # Customized port and number of threads

   edge.network.diag.iperf('192.168.1.145', direction=edge_enum.Traffic.Download)  # Measure download speed

   edge.network.diag.iperf('192.168.1.145', protocol=edge_enum.IPProtocol.UDP)  # Use UDP


Antivirus
=========

.. automethod:: cterasdk.edge.antivirus.Antivirus.enable
   :noindex:

.. code-block:: python

   edge.antivirus.settings.enable()

.. automethod:: cterasdk.edge.antivirus.Antivirus.disable
   :noindex:

.. code-block:: python

   edge.antivirus.settings.disable()

.. automethod:: cterasdk.edge.antivirus.Antivirus.update
   :noindex:

.. code-block:: python

   edge.antivirus.settings.update()

.. automethod:: cterasdk.edge.antivirus.Antivirus.status
   :noindex:

.. code-block:: python

   edge.antivirus.settings.status()

.. automethod:: cterasdk.edge.antivirus.Settings.get
   :noindex:

.. code-block:: python

   edge.antivirus.settings.get()

.. automethod:: cterasdk.edge.antivirus.Settings.update
   :noindex:

.. code-block:: python

   edge.antivirus.settings.update(edge_types.AntivirusUpdateSchedule.daily(5, 0))  # Daily at 5:00 am
   edge.antivirus.settings.update(edge_types.AntivirusUpdateSchedule.weekly(common_enum.DayOfWeek.Tuesday, 2, 15))  # Tuesdays at 2:15 am
   edge.antivirus.settings.update(edge_types.AntivirusUpdateSchedule.monthly(15, 15, 30))  # Every 15th at 3:30 pm


Ransomware Protection
=====================

.. automethod:: cterasdk.edge.ransom_protect.RansomProtect.get_configuration
   :noindex:

.. automethod:: cterasdk.edge.ransom_protect.RansomProtect.enable
   :noindex:

.. automethod:: cterasdk.edge.ransom_protect.RansomProtect.disable
   :noindex:

.. automethod:: cterasdk.edge.ransom_protect.RansomProtect.is_disabled
   :noindex:

.. automethod:: cterasdk.edge.ransom_protect.RansomProtect.modify
   :noindex:

.. automethod:: cterasdk.edge.ransom_protect.RansomProtect.incidents
   :noindex:

.. automethod:: cterasdk.edge.ransom_protect.RansomProtect.details
   :noindex:


Mail Server
===========

.. automethod:: cterasdk.edge.mail.Mail.enable
   :noindex:

.. code-block:: python

   edge.mail.enable('smtp.ctera.com') # default settings

   edge.mail.enable('smtp.ctera.com', 465) # custom port number

   """Use default port number, use authentication and require TLS"""

   edge.mail.enable('smtp.ctera.com', username='user', password='secret', useTLS=True)

   """Configure e-mail sender, recipients and minimum severity"""
   edge.mail.enable('smtp.ctera.com', username='user', password='secret', useTLS=True, sender='alert-no-reply@ctera.com', recipients=[
      'recipient_one@acme.com',
      'recipient_two@acme.com',
   ], min_severity=edge_enum.Severity.ERROR)

.. automethod:: cterasdk.edge.mail.Mail.disable
   :noindex:

.. code-block:: python

   edge.mail.disable()


Email Alerts
------------

.. automethod:: cterasdk.edge.mail.Alerts.get
   :noindex:

.. automethod:: cterasdk.edge.mail.Alerts.modify
   :noindex:

.. code-block:: python

   alerts = edge.mail.alerts.get()
   alerts.firmware_upgrade = True
   alerts.device_startup = True
   alerts.backup_success = False
   alerts.storage_volume_usage = True
   alerts.storage_volume_usage_percent = 85
   alerts.overdue_backup = False
   alerts.delayed_synchronization = True
   alerts.delayed_synchronization_hours = 1
   alerts.disconnected = True
   alerts.disconnected_hours = 1
   edge.mail.alerts.modify(alerts)

.. note:: See :py:class:`cterasdk.edge.types.AlertSettings` for alert description

Logging
=======

.. automethod:: cterasdk.edge.logs.Logs.settings
   :noindex:

.. automethod:: cterasdk.edge.logs.Logs.logs
   :noindex:

.. automethod:: cterasdk.edge.syslog.Syslog.enable
   :noindex:

.. code-block:: python

   edge.syslog.enable('syslog.ctera.com') # default settings

   edge.syslog.enable('syslog.ctera.com', proto = 'TCP') # use TCP

   edge.syslog.enable('syslog.ctera.com', 614, minSeverity = 'error') # use 614 UDP, severity >= error

.. automethod:: cterasdk.edge.syslog.Syslog.disable
   :noindex:

.. code-block:: python

   edge.syslog.disable()

CIFS/SMB Audit Logs
-------------------

.. automethod:: cterasdk.edge.audit.Audit.enable
   :noindex:

.. code-block:: python

   edge.audit.enable('/logs')

.. automethod:: cterasdk.edge.audit.Audit.disable
   :noindex:

.. code-block:: python

   edge.audit.disable()

Reset to Defaults
=================

.. automethod:: cterasdk.edge.power.Power.reset
   :noindex:

.. code-block:: python

   edge.power.reset() # will reset and immediately return
   edge.power.reset(wait=True) # will reset and wait for the Edge Filer to boot

.. seealso:: Create the first admin account after resetting the Edge Filer to its default settings: :py:func:`cterasdk.edge.users.Users.add_first_user()`

SSL Certificate
===============

SSL management commands supported starting Edge Filer v7.8 or higher:

.. automethod:: cterasdk.edge.ssl.ServerCertificate.get
   :noindex:

.. code-block:: python

   server_certificate = edge.ssl.server.get()
   print(server_certificate.fingerprint)

.. automethod:: cterasdk.edge.ssl.ServerCertificate.regenerate
   :noindex:

.. code-block:: python

   edge.ssl.server.regenerate()  # generate a self-signed server certificate

.. automethod:: cterasdk.edge.ssl.ServerCertificate.import_certificate
   :noindex:

.. code-block:: python

   edge.ssl.server.import_certificate(
      r'C:/users/username/certificate/private.key',
      r'C:/users/username/certificate/certificate.crt',
      r'C:/users/username/certificate/intermediate1.crt',
      r'C:/users/username/certificate/intermediate2.crt',
      r'C:/users/username/certificate/root.crt'
   )

.. automethod:: cterasdk.edge.ssl.TrustedCAs.all
   :noindex:

.. code-block:: python

   for ca_certificate in edge.ssl.ca.all():
       print(ca_certificate.fingerprint)

.. automethod:: cterasdk.edge.ssl.TrustedCAs.add
   :noindex:

.. code-block:: python

   edge.ssl.ca.add(r'C:/users/username/certificate/ca.crt')  # add Trusted CA certificate

.. automethod:: cterasdk.edge.ssl.TrustedCAs.remove
   :noindex:

.. code-block:: python

   certificate_fingerprint = '04:a0:56:a9:87:64:bb:dc:96:bf:6d:b0:49:fa:80:81:ed:06:8a:1e'
   edge.ssl.ca.remove(certificate_fingerprint)

.. automethod:: cterasdk.edge.ssl.TrustedCAs.clear
   :noindex:

.. code-block:: python

   edge.ssl.ca.clear()

SSL management commands supported up to Edge Filer v7.6:

.. automethod:: cterasdk.edge.ssl.SSLv1.get_storage_ca
   :noindex:

.. automethod:: cterasdk.edge.ssl.SSLv1.remove_storage_ca
   :noindex:

.. automethod:: cterasdk.edge.ssl.SSLv1.import_certificate
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
   edge.ssl.import_certificate(private_key, certificate, intermediate_cert, ca_certificate)

.. danger: Exercise caution. Test thoroughly prior to implementing in production. Ensure the integrity of the PEM encoded private key and certificates. Supplying an invalid private key or certificate will disable administrative access to the filer and would require CTERA Support to re-enable it.

SSL management commands supported in all Edge Filer versions:

.. automethod:: cterasdk.edge.ssl.SSL.disable_http
   :noindex:

.. code-block:: python

   edge.ssl.disable_http()

.. automethod:: cterasdk.edge.ssl.SSL.enable_http
   :noindex:

.. code-block:: python

   edge.ssl.enable_http()

.. automethod:: cterasdk.edge.ssl.SSL.is_http_disabled
   :noindex:

.. code-block:: python

   edge.ssl.is_http_disabled()

.. automethod:: cterasdk.edge.ssl.SSL.is_http_enabled
   :noindex:

.. code-block:: python

   edge.ssl.is_http_enabled()

Power Management
================

.. automethod:: cterasdk.edge.power.Power.reboot
   :noindex:

.. code-block:: python

   edge.power.reboot() # will reboot and immediately return

   edge.power.reboot(wait=True) # will reboot and wait

.. automethod:: cterasdk.edge.power.Power.shutdown
   :noindex:

.. code-block:: python

   edge.power.shutdown()


SNMP
====

.. automethod:: cterasdk.edge.snmp.SNMP.is_enabled
   :noindex:

.. code-block:: python

   edge.snmp.is_enabled()

.. automethod:: cterasdk.edge.snmp.SNMP.enable
   :noindex:

.. code-block:: python

   edge.snmp.enable(community_str='MpPcKl2sArSdTLZ4URj4')  # enable SNMP v2c
   edge.snmp.enable(username='snmp_user', auth_password='gVQBaHSOGV', privacy_password='VG0zbn5aJ')  # enable SNMP v3

.. automethod:: cterasdk.edge.snmp.SNMP.disable
   :noindex:

   edge.snmp.disable()

.. automethod:: cterasdk.edge.snmp.SNMP.modify
   :noindex:

   edge.snmp.modify(community_str='L0K2zGpgmOQH2CXaUSuB', username='snmp_user', auth_password='gVQBaHSOGV', privacy_password='VG0zbn5aJ')

.. automethod:: cterasdk.edge.snmp.SNMP.get_configuration
   :noindex:

   edge.snmp.get_configuration()

Troubleshooting
===============

Support Report
--------------

.. automethod:: cterasdk.edge.support.Support.get_support_report
   :noindex:

Debug Level
-----------

.. automethod:: cterasdk.edge.support.Support.set_debug_level
   :noindex:

.. code-block:: python

   edge.support.set_debug_level('backup', 'process', 'cttp', 'samba')
   edge.support.set_debug_level('info')
   edge.support.set_debug_level('caching', 'evictor')

Telnet
------

.. automethod:: cterasdk.edge.telnet.Telnet.enable
   :noindex:

.. code-block:: python

   edge.telnet.enable('a7df639a')

.. automethod:: cterasdk.edge.telnet.Telnet.disable
   :noindex:

.. code-block:: python

   edge.telnet.disable()

SSH
---

.. automethod:: cterasdk.edge.ssh.SSH.enable
   :noindex:

.. code-block:: python

   """Enable SSH access"""
   edge.ssh.enable()

   """Enable SSH access using a public key file"""
   edge.ssh.enable(public_key_file='./public_key.pub')  # relative to the current directory
   edge.ssh.enable(public_key_file='C:\\Users\\jsmith\\Desktop\\public_key.pub')  # full path

   """Generate an RSA key pair and enable SSH access"""

   from cryptography.hazmat.primitives.asymmetric import rsa
   from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

   private_key = rsa.generate_private_key(public_exponent=exponent, key_size=key_size)
   public_key = private_key.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH).decode('utf-8')

   edge.ssh.enable(public_key)

   """Print PEM-encoded RSA private key"""
   print(private_key.private_bytes(Encoding.PEM, PrivateFormat.OpenSSH, NoEncryption()).decode('utf-8'))

   """Print OpenSSH formatted RSA public key"""
   print(public_key)

.. automethod:: cterasdk.edge.ssh.SSH.disable
   :noindex:

.. code-block:: python

   edge.ssh.disable()

Miscellaneous
-------------

.. automethod:: cterasdk.objects.synchronous.edge.Edge.test
   :noindex:

.. code-block:: python

   edge.test()

.. automethod:: cterasdk.objects.synchronous.edge.Edge.whoami
   :noindex:

.. code-block:: python

   edge.whoami()
