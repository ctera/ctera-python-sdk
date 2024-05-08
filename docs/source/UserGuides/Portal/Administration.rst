=====================
Global Administration
=====================

Logging In
==========

.. automethod:: cterasdk.objects.core.GlobalAdmin.login
   :noindex:

.. code-block:: python

   admin.login('admin', 'G3neralZ0d!')

.. automethod:: cterasdk.objects.core.GlobalAdmin.logout
   :noindex:

.. code-block:: python

   admin.logout()

Browsing Tenants
================

.. automethod:: cterasdk.core.portals.Portals.browse_global_admin
   :noindex:

.. code-block:: python

   admin.portals.browse_global_admin()

.. automethod:: cterasdk.core.portals.Portals.browse
   :noindex:

.. code-block:: python

   admin.portals.browse('portal')

Managing Licenses
=================

.. automethod:: cterasdk.core.licenses.Licenses.all
   :noindex:

.. automethod:: cterasdk.core.licenses.Licenses.add
   :noindex:

.. code-block:: python

   admin.licenses.add('ABCD', 'EFGH', 'IJKL')

.. automethod:: cterasdk.core.licenses.Licenses.remove
   :noindex:

.. code-block:: python

   admin.licenses.remove('ABCD')


Storage Classes
===============

.. automethod:: cterasdk.core.storage_classes.StorageClasses.add
   :noindex:

.. code-block:: python

   admin.storage_classes.add('Archive')

.. automethod:: cterasdk.core.storage_classes.StorageClasses.all
   :noindex:


.. code-block:: python

   for storage_class in admin.storage_classes.all():
       print(storage_class)

.. automethod:: cterasdk.core.storage_classes.StorageClasses.get
   :noindex:

.. code-block:: python

   print(admin.storage_classes.get('Archive'))


Managing Storage Nodes
======================

.. automethod:: cterasdk.core.buckets.Buckets.get
   :noindex:

.. code-block:: python

   bucket = admin.buckets.get('MainStorage')
   print(bucket)

   bucket = admin.buckets.get('MainStorage', include=['bucket', 'driver'])
   print(bucket.name, bucket.bucket, bucket.driver)

.. automethod:: cterasdk.core.buckets.Buckets.add
   :noindex:

.. code-block:: python

   """Add an Amazon S3 bucket called 'mybucket'"""
   bucket = core_types.AmazonS3('mybucket', 'access-key', 'secret-key')
   admin.buckets.add('cterabucket', bucket)

   """Add an Amazon S3 bucket called 'mybucket', dedicated to a tenant called 'mytenant'"""
   bucket = core_types.AmazonS3('mybucket', 'access-key', 'secret-key')
   admin.buckets.add('cterabucket', bucket, dedicated_to='mytenant')

   """Add a bucket in read-delete only mode"""
   bucket = core_types.AmazonS3('mybucket', 'access-key', 'secret-key')
   admin.buckets.add('cterabucket', bucket, read_only=True)

.. automethod:: cterasdk.core.buckets.Buckets.modify
   :noindex:

.. code-block:: python

   """Modify an existing bucket, set it to read-delete only and dedicate it to 'mytenant'"""
   admin.buckets.modify('MainStorage', read_only=True, dedicated_to='mytenant')

.. automethod:: cterasdk.core.buckets.Buckets.list_buckets
   :noindex:

.. code-block:: python

   for bucket in admin.buckets.list_buckets():
       print(bucket)

.. automethod:: cterasdk.core.buckets.Buckets.delete
   :noindex:

.. code-block:: python

   admin.buckets.delete('MainStorage')

.. automethod:: cterasdk.core.buckets.Buckets.read_write
   :noindex:

.. code-block:: python

   admin.buckets.read_write('MainStorage')

.. automethod:: cterasdk.core.buckets.Buckets.read_only
   :noindex:

.. code-block:: python

   admin.buckets.read_only('MainStorage')


Managing Portals
================

Querying
--------

.. automethod:: cterasdk.core.portals.Portals.list_tenants
   :noindex:

.. code-block:: python

   """List all tenants"""
   for tenant in admin.portals.list_tenants():
       print(tenant)

   """List Team Portals. For each tenant, retrieve its creation date, subscription plan and activation status"""
   for tenant in admin.portals.list_tenants(include=['createDate', 'plan', 'activationStatus'], portal_type=core_enum.PortalType.Team):
       print(tenant)

.. automethod:: cterasdk.core.portals.Portals.tenants
   :noindex:

.. code-block:: python

   for tenant in admin.portals.tenants():
       print(tenant.name, tenant.usedStorageQuota, tenant.totalStorageQuota)

Creating a Team Portal
----------------------

.. automethod:: cterasdk.core.portals.Portals.add
   :noindex:

.. code-block:: python

   """Create a Team Portal"""

   admin.portals.add('acme')

   """Create a Team Portal, including a display name, billing id and a company name"""

   admin.portals.add('ctera', 'CTERA', 'Tz9YRDSd8LNfaouzr3Db', 'CTERA Networks')

   """Create a Team Portal and assign it to a pre-configured subscription plan"""
   admin.portals.add('ctera', plan = 'Default')

Subcribing a Portal to a Plan
-----------------------------

.. automethod:: cterasdk.core.portals.Portals.subscribe
   :noindex:

.. code-block:: python

   admin.portals.subscribe('ctera', '10tb')

Apply Provisioning Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.core.portals.Portals.apply_changes
   :noindex:

.. code-block:: python

   """Apply Portal Provisioning Changes"""
   admin.portals.apply_changes()
   admin.portals.apply_changes(wait=True)  # wait for all changes to apply

   """Apply User Provisioning Changes"""
   admin.users.apply_changes()
   admin.users.apply_changes(wait=True)  # wait for all changes to apply

Delete a Team Portal
--------------------

.. automethod:: cterasdk.core.portals.Portals.delete
   :noindex:

.. code-block:: python

   admin.portals.delete_tenant('acme')

Recover a Team Portal
---------------------

.. automethod:: cterasdk.core.portals.Portals.undelete
   :noindex:

.. code-block:: python

   admin.portals.undelete_tenant('acme')

Subscription Plans
==================

.. automethod:: cterasdk.core.plans.Plans.get
   :noindex:

.. code-block:: python

   plan = admin.plans.get('good_plan', ['createDate', 'modifiedDate'])

.. automethod:: cterasdk.core.plans.Plans.list_plans
   :noindex:

.. code-block:: python

   """List plans and include their creation date"""
   for plan in admin.plans.list_plans(['createDate']):
       print(plan)

.. automethod:: cterasdk.core.plans.Plans.by_name
   :noindex:

.. code-block:: python

   """List plans 'PlanOne' and 'PlanTwo'; and retrieve the 'modifiedDate', 'uid' and 'isDefault' properties"""
   for plan in admin.plans.by_name(['PlanOne', 'PlanTwo'], ['modifiedDate', 'uid', 'isDefault']):
       print(plan)

.. automethod:: cterasdk.core.plans.Plans.add
   :noindex:

.. code-block:: python

   """
   Retention Policy (core_enum.PlanRetention):
   - All: All Versions
   - Hourly: Hourly Versions
   - Daily: Daily Versions
   - Weekly: Weekly Versions
   - Monthly: Monthly Versions
   - Quarterly: Quarterly Versions
   - Yearly: Yearly Versions
   - Deleted: Recycle Bin

   Quotas (core_enum.PlanItem):
   - Storage: Storage Quota, in Gigabytes
   - EV4: CTERA Edge Filer, Up to 4 TB of Local Cache
   - EV8: CTERA Edge Filer, Up to 8 TB of Local Cache
   - EV16: CTERA Edge Filer, Up to 16 TB of Local Cache
   - EV32: CTERA Edge Filer, Up to 32 TB of Local Cache
   - EV64: CTERA Edge Filer, Up to 64 TB of Local Cache
   - EV128: CTERA Edge Filer, Up to 128 TB of Local Cache
   - WA: Workstation Backup Agent
   - SA: Server Agent
   - Share: CTERA Drive Share
   - Connect: CTERA Drive Connect
   """

   """
   Create the 'good_plan' subscription plan:
   1) Retention: 7 daily versions, 12 monthly versions
   2) Quotas: 10 x EV16, 5 x EV32, 100 x Cloud Drive (Share)
   """

   name = 'good_plan'
   services = {core_enum.PlanService.CloudBackup: core_enum.PlanServiceState.Disabled, core_enum.PlanService.CloudDrive: core_enum.PlanServiceState.Disabled}
   retention = {core_enum.PlanRetention.Daily: 7, core_enum.PlanRetention.Monthly: 12}
   quotas = {core_enum.PlanItem.EV16: 10, core_enum.PlanItem.EV32: 5, core_enum.PlanItem.Share: 100}
   admin.plans.add(name, services, retention, quotas)

.. automethod:: cterasdk.core.plans.Plans.modify
   :noindex:

.. code-block:: python

   """
   Modify 'good_plan' subscription plan:
   1) Retention: 30 daily versions, 36 monthly versions
   2) Quotas: 20 x EV16, 10 x EV32, 200 x Cloud Drive (Share)
   """

   name = 'good_plan'
   services = {core_enum.PlanService.CloudBackup: core_enum.PlanServiceState.Disabled, core_enum.PlanService.CloudDrive: core_enum.PlanServiceState.Disabled}
   retention = {core_enum.PlanRetention.Daily: 30, core_enum.PlanRetention.Monthly: 36}
   quotas = {core_enum.PlanItem.EV16: 20, core_enum.PlanItem.EV32: 10, core_enum.PlanItem.Share: 200}
   admin.plans.modify(name, services, retention, quotas)

.. automethod:: cterasdk.core.plans.Plans.delete
   :noindex:

.. code-block:: python

   name = 'good_plan'
   admin.plan.delete(name)

Plan Auto Assignment Rules
--------------------------

.. automethod:: cterasdk.core.plans.PlanAutoAssignPolicy.get_policy
   :noindex:

.. automethod:: cterasdk.core.plans.PlanAutoAssignPolicy.set_policy
   :noindex:

.. code-block:: python

   """Apply the '100GB' plan to all user names that start with 'adm'"""
   c1 = core_types.PlanCriteriaBuilder.username().startswith('adm').build()
   r1 = PolicyRule('100GB', c1)

   """Apply the '200GB' plan to all user names that end with 'inc'"""
   c2 = core_types.PlanCriteriaBuilder.username().endswith('inc').build()
   r2 = PolicyRule('200GB', c2)

   """Apply the 'Bingo' plan to all user names that contain 'bing'"""
   c3 = core_types.PlanCriteriaBuilder.username().contains('bing').build()
   r3 = PolicyRule('Bingo', c3)

   """Apply the 'ABC' plan to 'alice', 'bob' and 'charlie'"""
   c4 = core_types.PlanCriteriaBuilder.username().isoneof(['alice', 'bob', 'charlie']).build()
   r4 = PolicyRule('ABC', c4)

   """Apply the '10TB' plan to read write, read only and support administrators"""
   roles = [core_enum.Role.ReadWriteAdmin, core_enum.Role.ReadOnlyAdmin, core_enum.Role.Support]
   c5 = core_types.PlanCriteriaBuilder.role().include(roles).build()
   r5 = PolicyRule('10TB', c5)

   """Apply the 'TechStaff' plan to the 'Product' and 'Support' groups"""
   c6 = core_types.PlanCriteriaBuilder.user_groups().include(['Product', 'Support']).build()
   r6 = PolicyRule('TechStaff', c6)

   admin.plans.auto_assign.set_policy([r1, r2, r3, r4, r5, r6])

   """Remove all policy rules"""
   admin.plans.auto_assign.set_policy([])

   """Do not assign a default plan if no match applies"""
   admin.plans.auto_assign.set_policy([], False)

   """Assign 'Default' if no match applies"""
   admin.plans.auto_assign.set_policy([], True, 'Default')

Configuration Templates
=======================

.. automethod:: cterasdk.core.templates.Templates.get
   :noindex:

.. code-block:: python

   admin.templates.get('MyTemplate')

.. automethod:: cterasdk.core.templates.Templates.list_templates
   :noindex:

.. code-block:: python

   for template in admin.templates.list_templates(include=['name', 'description', 'modifiedDate']):
       print(template.name, template.description, template.modifiedDate)

.. automethod:: cterasdk.core.templates.Templates.add
   :noindex:

   This library provides several classes, methods and enumerators to assist in creating configuration templates:
   #. Builder class for filtered backup sets. :py:class:`cterasdk.common.types.FileFilterBuilder`
   #. A class representing a backup include or exclude set. :py:class:`cterasdk.common.types.FilterBackupSet`
   #. Builder class for defining backup schedule. :py:class:`cterasdk.common.types.BackupScheduleBuilder`
   #. A time-range class, used to configure backups to run at a specific time. :py:class:`cterasdk.common.types.TimeRange`
   #. Enumerator containing applications supported for backup. :py:class:`cterasdk.common.enum.Application`
   #. A named tuple defining a platform and a software version. :py:class:`cterasdk.core.types.PlatformVersion`
   #. Enumerator containing a list of platforms. :py:class:`cterasdk.core.enum.Platform`

.. code-block:: python

   """Include all 'pptx', 'xlsx' and 'docx' file types for all users"""
   docs = common_types.FileFilterBuilder.extensions().include(['pptx', 'xlsx', 'docx']).build()
   include_sets = common_types.FilterBackupSet('Documents', filter_rules=[docs],
                                                         template_dirs=[core_enum.EnvironmentVariables.ALLUSERSPROFILE])

   """Exclude all 'cmd', 'exe' and 'bat' file types for all users"""
   programs = common_types.FileFilterBuilder.extensions().include(['cmd', 'exe', 'bat']).build()
   exclude_sets = common_types.FilterBackupSet('Programs', filter_rules=[programs],
                                                           template_dirs=[core_enum.EnvironmentVariables.ALLUSERSPROFILE])

   """Schedule backup to run periodically"""
   backup_schedule = common_types.BackupScheduleBuilder.interval(hours=6)  # periodically, every 6 hours
   backup_schedule = common_types.BackupScheduleBuilder.interval(hours=0, minutes=30)  # periodically, every 30 minutes

   """Schedule backup for a specific time"""
   time_range = common_types.TimeRange().start('07:00:00').days(common_enum.DayOfWeek.Weekdays).build()  # 7am, on weekdays
   backup_schedule = common_types.BackupScheduleBuilder.window(time_range)

   """Backup applications"""
   apps = [common_enum.Application.NTDS, common_enum.Application.HyperV]  # back up Active Directory and Hyper-V
   apps = common_enum.Application.All  # back up all applications

   """Configure software versions"""
   versions = [core_types.PlatformVersion(core_enum.Platform.Edge_7, '7.0.981.7')]  # use 7.0.981.7 for v7 Edge Filers

   """Configure software update schedule"""
   schedule = common_types.TimeRange().start('01:00:00').end('02:00:00').days(common_enum.DayOfWeek.Weekdays).build()
   builder = common_types.SoftwareUpdatePolicyBuilder()
   update_settings = builder.download_and_install(True).reboot_after_update(True).schedule(schedule).build()

   """Configure Scripts"""
   scripts = [
       core_types.TemplateScript.windows().after_logon('echo Current directory: %cd%'),
       core_types.TemplateScript.linux().before_backup('./mysqldump -u admin website > /mnt/backup/backup.sql'),
       core_types.TemplateScript.linux().after_backup('rm /mnt/backup/backup.sql')
   ]

   """Configure CLI Commands"""
   cli_commands = [
       'set /config/agent/stubs/deleteFilesOfCachedFolderOnDisable false',
       'add /config/agent/stubs/allowedExplorerExtensions url'
   ]

   """Configure Consent Page"""
   consent_page = common_types.ConsentPage('the header of your consent page', 'the body of your consent page')

   admin.templates.add('MyTemplate', 'woohoo', include_sets=[include_sets], exclude_sets=[exclude_sets],
                      backup_schedule=backup_schedule, apps=apps, versions=versions, update_settings=update_settings,
                      scripts=scripts, cli_commands=cli_commands, consent_page=consent_page)

.. automethod:: cterasdk.core.templates.Templates.set_default
   :noindex:

.. code-block:: python

   admin.templates.set_default('MyTemplate')

   admin.templates.set_default('MyTemplate', wait=True)  # wait for template changes to apply

.. automethod:: cterasdk.core.templates.Templates.remove_default
   :noindex:

.. code-block:: python

   admin.templates.remove_default('MyTemplate')

   admin.templates.remove_default('MyTemplate', wait=True)  # wait for template changes to apply

.. automethod:: cterasdk.core.templates.TemplateAutoAssignPolicy.apply_changes
   :noindex:

.. code-block:: python

   admin.templates.auto_assign.apply_changes()

   admin.templates.auto_assign.apply_changes(wait=True)  # wait for template changes to apply

Template Auto Assignment Rules
------------------------------

.. automethod:: cterasdk.core.templates.TemplateAutoAssignPolicy.get_policy
   :noindex:

.. automethod:: cterasdk.core.templates.TemplateAutoAssignPolicy.set_policy
   :noindex:

.. code-block:: python

   """Apply the 'ESeries' template to devices of type: C200, C400, C800, C800P"""
   device_types = [core_enum.DeviceType.C200, core_enum.DeviceType.C400, core_enum.DeviceType.C800, core_enum.DeviceType.C800P]
   c1 = core_types.TemplateCriteriaBuilder.type().include(device_types).build()
   r1 = PolicyRule('ESeries', c1)

   """Apply the 'Windows' template to devices that use a 'Windows' operating system"""
   c2 = core_types.TemplateCriteriaBuilder.os().contains('Windows').build()
   r2 = PolicyRule('Windows', c2)

   """Apply the 'CTERA7' template to devices running version 7"""
   c3 = core_types.TemplateCriteriaBuilder.version().startswith('7.0').build()
   r3 = PolicyRule('CTERA7', c3)

   """Apply the 'WD5' template to devices that their hostname ends with 'WD5'"""
   c4 = core_types.TemplateCriteriaBuilder.hostname().endswith('WD5').build()
   r4 = PolicyRule('WD5', c4)

   """Apply the 'Beta' template to devices that their name is one of"""
   c5 = core_types.TemplateCriteriaBuilder.name().isoneof(['DEV1', 'DEV2', 'DEV3']).build()
   r5 = PolicyRule('Beta', c5)

   admin.templates.auto_assign.set_policy([r1, r2, r3, r4, r5])

   """Remove all policy rules"""
   admin.templates.auto_assign.set_policy([])

   """Do not assign a default template if no match applies"""
   admin.templates.auto_assign.set_policy([], False)

   """Assign 'Default' if no match applies"""
   admin.templates.auto_assign.set_policy([], True, 'Default')

Portal Servers
==============

.. automethod:: cterasdk.core.servers.Servers.get
   :noindex:

.. code-block:: python

   """Retrieve a server"""

   server = admin.servers.get('server', ['isApplicationServer', 'renderingServer'])
   print(server.isApplicationServer, server.renderingServer)

.. automethod:: cterasdk.core.servers.Servers.list_servers
   :noindex:

.. code-block:: python

   """Retrieve all servers"""
   servers = admin.servers.list_servers() # will only retrieve the server name
   for server in servers:
       print(server.name)

   """Retrieve multiple server attributes"""
   servers = admin.servers.list_servers(include = ['name', 'connected', 'isApplicationServer', 'mainDB'])
   for server in servers:
       print(server)

.. automethod:: cterasdk.core.servers.Servers.modify
   :noindex:

.. code-block:: python

   admin.servers.modify('server2', server_name='replica', app=False, enable_replication=True, replica_of='maindb')  # rename and enable database replication

   admin.servers.modify('server2', allow_user_login=False)  # disable logins to this server

   admin.servers.modify('server2', enable_public_ip=True, public_ip='33.191.55.2')  # configure a public NAT ip address

Server Tasks
------------

.. automethod:: cterasdk.core.servers.Tasks.background
   :noindex:

.. code-block:: python

   for task in admin.servers.tasks.background('database'):
       print(task.name)

.. automethod:: cterasdk.core.servers.Tasks.scheduled
   :noindex:

.. code-block:: python

   for task in admin.servers.tasks.scheduled('database'):
      print(task.name)

Messaging Service
=================

.. automethod:: cterasdk.core.messaging.Messaging.get_status
   :noindex:

.. code-block:: python

   """Retrieve the global status of Messaging service"""

   print(admin.messaging.get_status())

.. automethod:: cterasdk.core.messaging.Messaging.get_servers_status
   :noindex:

.. code-block:: python

   """Retrieve the status of the Messaging servers"""

   print(admin.messaging.get_servers_status())

.. automethod:: cterasdk.core.messaging.Messaging.add
   :noindex:

.. code-block:: python

   """Add Messaging servers to cluster"""

   servers = ["server1", "server2", "server3"]
   admin.messaging.add(servers)

Key Management Service
======================

.. automethod:: cterasdk.core.kms.KMS.settings
   :noindex:

.. code-block:: python

   admin.kms.settings()

.. automethod:: cterasdk.core.kms.KMS.status
   :noindex:

.. code-block:: python

   admin.kms.status()

.. automethod:: cterasdk.core.kms.KMS.enable
   :noindex:

.. code-block:: python

   private_key = './private_key.pem'
   client_certificate = './client_certificate.crt'
   server_certificate = './server_certificate.crt'

   admin.kms.enable(private_key, client_certificate, server_certificate)

.. automethod:: cterasdk.core.kms.KMS.disable
   :noindex:

.. code-block:: python

   admin.kms.disable()

.. automethod:: cterasdk.core.kms.KMS.modify
   :noindex:

Key Management Service Servers
------------------------------

.. automethod:: cterasdk.core.kms.KMSServers.get
   :noindex:

.. code-block:: python

   admin.kms.servers.get('kms001')

.. automethod:: cterasdk.core.kms.KMSServers.all
   :noindex:

.. code-block:: python

   for server in admin.kms.servers.all():
       print(server)

.. automethod:: cterasdk.core.kms.KMSServers.add
   :noindex:

.. code-block:: python

   admin.kms.servers.add('kms001', '192.168.30.1')

.. automethod:: cterasdk.core.kms.KMSServers.modify
   :noindex:

.. code-block:: python

   admin.kms.servers.modify('kms001', 'kms001-renamed')

.. automethod:: cterasdk.core.kms.KMSServers.delete
   :noindex:

.. code-block:: python

   admin.kms.servers.delete('kms001')


Antivirus
=========

.. automethod:: cterasdk.core.antivirus.Antivirus.list_servers
   :noindex:

.. automethod:: cterasdk.core.antivirus.Antivirus.status
   :noindex:

.. automethod:: cterasdk.core.antivirus.Antivirus.rescan
   :noindex:

.. automethod:: cterasdk.core.antivirus.Antivirus.suspend
   :noindex:

.. automethod:: cterasdk.core.antivirus.Antivirus.unsuspend
   :noindex:

Antivirus Servers
-----------------

.. automethod:: cterasdk.core.antivirus.AntivirusServers.get
   :noindex:

.. automethod:: cterasdk.core.antivirus.AntivirusServers.add
   :noindex:

.. automethod:: cterasdk.core.antivirus.AntivirusServers.delete
   :noindex:

.. automethod:: cterasdk.core.antivirus.AntivirusServers.suspend
   :noindex:

.. automethod:: cterasdk.core.antivirus.AntivirusServers.unsuspend
   :noindex:


Global Administrators
=====================

.. automethod:: cterasdk.core.admins.Administrators.list_admins
   :noindex:

.. code-block:: python

   """list all global admins"""
   for admin in admin.admins.list_global_administrators():
       print(admin.name)

   for admin in admin.admins.list_global_administrators(include=['name', 'email', 'firstName', 'lastName']):
       print(admin)

.. automethod:: cterasdk.core.admins.Administrators.add
   :noindex:

.. code-block:: python

   """Create a global admin"""
   admin.admins.add('bruce', 'bruce.wayne@we.com', 'Bruce', 'Wayne', 'G0th4amCity!')

.. automethod:: cterasdk.core.admins.Administrators.modify
   :noindex:

.. code-block:: python

   """Modify a global admin"""
   admin.admins.modify('bruce', 'bwayne@we.com', 'Bruce', 'Wayne', 'Str0ngP@ssword!', 'Wayne Enterprises')


.. automethod:: cterasdk.core.admins.Administrators.delete
   :noindex:

.. code-block:: python

   """Delete a global admin"""
   admin.admins.delete('alice')


User Roles
==========

.. automethod:: cterasdk.core.roles.Roles.types
   :noindex:

.. code-block:: python

   print(admin.roles.types)

.. automethod:: cterasdk.core.roles.Roles.get
   :noindex:

.. code-block:: python

   rw_admin_settings = admin.roles.get(core_enum.Role.ReadWriteAdmin)
   ro_admin_settings = admin.roles.get(core_enum.Role.ReadOnlyAdmin)
   support_admin_settings = admin.roles.get(core_enum.Role.Support)

.. automethod:: cterasdk.core.roles.Roles.modify
   :noindex:

.. code-block:: python

   support_admin_settings = admin.roles.get(core_enum.Role.Support)
   support_admin_settings.manage_logs = True
   admin.roles.modify(core_enum.Role.Support, support_admin_settings)

Users
=====

.. automethod:: cterasdk.core.users.Users.delete
   :noindex:

.. code-block:: python

   """Delete a local user"""

   alice = core_types.UserAccount('alice')
   admin.users.delete(alice)

   """Delete a domain user"""

   bruce = core_types.UserAccount('bruce', 'domain.ctera.local')
   admin.users.delete(bruce)

Local Users
-----------

.. automethod:: cterasdk.core.users.Users.list_local_users
   :noindex:

.. code-block:: python

   users = admin.users.list_local_users()

   for user in users:

       print(user.name)

   users = admin.users.list_local_users(include = ['name', 'email', 'firstName', 'lastName'])

   for user in users:

       print(user)

.. automethod:: cterasdk.core.users.Users.add
   :noindex:

.. code-block:: python

   """Create a local user"""
   admin.users.add('bruce', 'bruce.wayne@we.com', 'Bruce', 'Wayne', 'G0th4amCity!')

.. automethod:: cterasdk.core.users.Users.modify
   :noindex:

.. code-block:: python

   """Modify a local user"""
   admin.users.modify('bruce', 'bwayne@we.com', 'Bruce', 'Wayne', 'Str0ngP@ssword!', 'Wayne Enterprises')

Domain Users
------------

.. automethod:: cterasdk.core.users.Users.list_domain_users
   :noindex:

.. code-block:: python

   users = admin.users.list_domain_users('domain.ctera.local') # will only retrieve the 'name' attribute
   for user in users:
       print(user.name)

   """Retrieve additional user attributes"""
   users = admin.users.list_domain_users('domain.ctera.local', include = ['name', 'email', 'firstName', 'lastName'])
   print(user)

Fetch Users & Groups
^^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.core.directoryservice.DirectoryService.fetch
   :noindex:

.. code-block:: python

   """Fetch domain users"""

   alice = core_types.UserAccount('alice', 'domain.ctera.local')
   bruce = core_types.UserAccount('bruce', 'domain.ctera.local')

   admin.directoryservice.fetch([alice, bruce])

Directory Services
==================

.. automethod:: cterasdk.core.directoryservice.DirectoryService.connect
   :noindex:

.. code-block:: python

   """Connect to Active Directory using a primary domain controller, configure domain UID/GID mapping and access control"""
   mapping = [core_types.ADDomainIDMapping('demo.local', 200001, 5000000), core_types.ADDomainIDMapping('trusted.local', 5000001, 10000000)]
   rw_admin_group = core_types.AccessControlEntry(
       core_types.GroupAccount('ctera_admins', 'demo.local'),
       core_enum.Role.ReadWriteAdmin
   )
   ro_admin_user = core_types.AccessControlEntry(
       core_types.UserAccount('jsmith', 'demo.local'),
       core_enum.Role.ReadOnlyAdmin
   )
   admin.directoryservice.connect('demo.local', 'svc_account', 'P@ssw0rd1', mapping=mapping, domain_controllers=core_types.DomainControllers('172.54.3.52'), acl=[rw_admin, ro_admin])

.. automethod:: cterasdk.core.directoryservice.DirectoryService.domains
   :noindex:

.. code-block:: python

   print(admin.directoryservice.domains())


.. automethod:: cterasdk.core.directoryservice.DirectoryService.get_connected_domain
   :noindex:

.. code-block:: python

   print(admin.directoryservice.get_connected_domain())

.. automethod:: cterasdk.core.directoryservice.DirectoryService.get_advanced_mapping
   :noindex:

.. code-block:: python

   for domain, mapping in admin.directoryservice.get_advanced_mapping().items():
       print(domain, mapping)

.. automethod:: cterasdk.core.directoryservice.DirectoryService.set_advanced_mapping
   :noindex:

.. code-block:: python

   """Configure UID/GID mapping"""
   mapping = [core_types.ADDomainIDMapping('demo.local', 200001, 5000000), core_types.ADDomainIDMapping('trusted.local', 5000001, 10000000)]
   admin.directoryservice.set_advanced_mapping(mapping)

.. automethod:: cterasdk.core.directoryservice.DirectoryService.get_access_control
   :noindex:

.. code-block:: python

   for ace in admin.directoryservice.get_access_control():
       print(ace.account, ace.role)

.. automethod:: cterasdk.core.directoryservice.DirectoryService.set_access_control
   :noindex:

.. code-block:: python

   """Configure access control for a domain group and a domain user. Set the default role to 'Disabled'"""
   rw_admin_group = core_types.AccessControlEntry(
       core_types.GroupAccount('ctera_admins', 'demo.local'),
       core_enum.Role.ReadWriteAdmin
   )
   ro_admin_user = core_types.AccessControlEntry(
       core_types.UserAccount('jsmith', 'demo.local'),
       core_enum.Role.ReadOnlyAdmin
   )
   admin.directoryservice.set_access_control([rw_admin_group, ro_admin_user], core_enum.Role.Disabled)

.. automethod:: cterasdk.core.directoryservice.DirectoryService.get_default_role

.. code-block:: python

   print(admin.directoryservice.get_default_role())

.. automethod:: cterasdk.core.directoryservice.DirectoryService.disconnect
   :noindex:

.. code-block:: python

   admin.directoryservice.disconnect()


Managing S3 Credentials
=======================

.. automethod:: cterasdk.core.credentials.S3.all
   :noindex:

.. code-block:: python

   """List all of 'jsmith@demo.local' S3 credentials"""
   jsmith = core_types.UserAccount('jsmith', 'demo.local')
   for credential in user.credentials.s3.all(jsmith):
       print(credential.accessKey, credential.activated)

.. automethod:: cterasdk.core.credentials.S3.create
   :noindex:

.. code-block:: python

   """Create an S3 credential for a service account"""
   service_account = core_types.UserAccount('service_account')
   credential = user.credentials.s3.create(service_account)

.. automethod:: cterasdk.core.credentials.S3.delete
   :noindex:

.. code-block:: python

   """Delete an S3 credentials associated with a user account"""
   user_account = core_types.UserAccount('jsmith', 'demo.local')
   access_key_id = 'ABCDEFGHIJKLMOP'
   user.credentials.s3.delete(access_key_id, user_account)

Managing Groups
===============

.. automethod:: cterasdk.core.groups.Groups.delete
   :noindex:

.. code-block:: python

   """Delete a local group"""
   group = core_types.GroupAccount('local_group')
   admin.groups.delete(group)

   """Delete a domain group"""

   group = core_types.GroupAccount('domain_group', 'domain.ctera.local')
   admin.groups.delete(group)

Local Groups
------------

.. automethod:: cterasdk.core.groups.Groups.list_local_groups
   :noindex:

.. code-block:: python

   groups = admin.groups.list_local_groups()
   for group in groups:
       print(group.name)

   groups = admin.groups.list_local_groups(include=['name', 'description'])
   for group in groups:
       print(group)

.. automethod:: cterasdk.core.groups.Groups.add
   :noindex:

.. code-block:: python

   """Create a local group"""
   admin.groups.add('Users')
   admin.groups.add('Users', 'A group of users')  # with description
   admin.groups.add('Users', members=[core_types.UserAccount('alice'), core_types.UserAccount('bruce', 'domain.ctera.local')])  # with members

.. automethod:: cterasdk.core.groups.Groups.modify
   :noindex:

.. code-block:: python

   """Modify a local group"""
   admin.groups.modify('Users', new_groupname='End Users')  # change group name
   admin.groups.modify('Users', description='A group of end users')  # change group description

.. automethod:: cterasdk.core.groups.Groups.get_members
   :noindex:

.. code-block:: python

   """Get group members"""
   admin.groups.get_members(core_types.GroupAccount('Users'))  # get members of a local group
   admin.groups.get_members(core_types.GroupAccount('Users', 'domain.ctera.local'))  # get members of a domain group

.. automethod:: cterasdk.core.groups.Groups.add_members
   :noindex:

.. code-block:: python

   """Add group members"""
   admin.groups.add_members(core_types.GroupAccount('Users'), [core_types.UserAccount('alice')])  # add local users to a local group
   admin.groups.add_members(core_types.GroupAccount('Users'), [core_types.UserAccount('bruce', 'domain.ctera.local')])  # add domain users to a local group


Devices
=======

.. automethod:: cterasdk.core.devices.Devices.device
   :noindex:

.. automethod:: cterasdk.core.devices.Devices.filers
   :noindex:

.. code-block:: python

   """Retrieve all Gateways from the current tenant"""

   filers = admin.devices.filers()
   for filer in filers:
       print(filer.name) # will print the Gateway name

   """Retrieve additional Gateway attributes"""
   filers = admin.devices.filers(['owner', 'deviceConnectionStatus'])

   """Retrieve nested attributes using the '.' delimiter"""
   filers = admin.devices.filers(['deviceReportedStatus.status.device.runningFirmware'])

   """Retrieve filers from all portals"""
   admin.portals.browse_global_admin()

   filers = admin.devices.filers(allPortals = True)
   """Retrieve C200's and C400's from all portals"""
   admin.portals.browse_global_admin()
   filers = admin.devices.filers(allPortals = True, deviceTypes = ['C200', 'C400'])

.. automethod:: cterasdk.core.devices.Devices.agents
   :noindex:

.. code-block:: python

   """Retrieve all Agents from the current tenant"""
   agents = admin.devices.agents()
   for agent in agents:
       print(agent.name) # will print the Agent name

   """Retrieve all Agents and the underlying OS name"""
   agents = admin.devices.agents(['deviceReportedStatus.status.agent.details.osName'])

.. automethod:: cterasdk.core.devices.Devices.servers
   :noindex:

.. code-block:: python

   server_agents = admin.devices.servers()

.. automethod:: cterasdk.core.devices.Devices.desktops
   :noindex:

.. code-block:: python

   desktop_agents = admin.devices.desktop_agents()

.. automethod:: cterasdk.core.devices.Devices.by_name
   :noindex:

.. automethod:: cterasdk.core.devices.Devices.get_comment
   :noindex:

.. code-block:: python

   print(admin.devices.get_comment('FSRV'))

.. automethod:: cterasdk.core.devices.Devices.set_comment
   :noindex:

.. code-block:: python

   admin.devices.set_comment('FSRV', 'Production')


Remote Access
=============

The Devices APIs retrieve a handle that can be used to query and update the configuration of remote Edge Filers or Drive Agents.

.. code-block:: python

    """Retrieving a List of Shares from an Edge Filer"""
    edge = admin.devices.device('edge-hostname')
    shares = edge.shares.get()
    for share in shares:
        print(share.name)

The handle retrieved from the Portal provides limited access to the Edge Filer or Drive Agent APIs.
To obtain access to the full set of APIs, use the ``remote_access`` function.

.. automethod:: cterasdk.objects.edge.Edge.remote_access
   :noindex:

.. code-block:: python

   """Retrieving a List of Shares from an Edge Filer"""

   edge = admin.devices.device('edge-hostname')
   remote_session = edge.remote_access()  # Returns an authenticated remote access session

   """Downloading a File via a Remote Access Edge Filer Session"""
   remote_session.files.download('cloud/users/Service Account/My Files/docs/document.docx')


Device Activation Codes
=======================
.. automethod:: cterasdk.core.activation.Activation.generate_code
   :noindex:

.. code-block:: python

   """Generate a device activation code"""
   code = admin.activation.generate_code() # will generate a code for the current, logged on, user
   code = admin.activation.generate_code('bruce') # will generate a code for 'bruce' in the current tenant
   code = admin.activation.generate_code('batman', 'gotham') # will generate a code for 'bruce' in the 'gotham' tenant

.. note:: Read Write Administrator, granted with the "Super User" role permission, can generate 200 codes every 5 minutes

Reports
=======

Generate a Report
-----------------

.. automethod:: cterasdk.core.reports.Reports.generate
   :noindex:

Reports may take a while to generate, use the following commands to trigger the execution of the reports.

.. code-block:: python

   """Global Administration"""
   admin.reports.generate(core_enum.Reports.Storage)
   admin.reports.generate(core_enum.Reports.Portals)

   """Team Portal"""
   admin.reports.generate(core_enum.Reports.Folders)
   admin.reports.generate(core_enum.Reports.FolderGroups)

Retrieve a Report
-----------------

Once a report was generated, use the following commands to retrieve the report.

.. automethod:: cterasdk.core.reports.Reports.storage
   :noindex:

.. automethod:: cterasdk.core.reports.Reports.portals
   :noindex:

.. automethod:: cterasdk.core.reports.Reports.folders
   :noindex:

.. automethod:: cterasdk.core.reports.Reports.folder_groups
   :noindex:


Managing the CTERA Global Namespace
===================================

Folder Groups
-------------

.. automethod:: cterasdk.core.cloudfs.FolderGroups.all
   :noindex:

.. code:: python

   """List all folder groups"""
   folder_groups = admin.cloudfs.groups.all()
   for folder_group in folder_groups:
       print(folder_group.name, folder_group.owner)

   """List folder groups owned by a domain user"""
   bruce = core_types.UserAccount('bruce', 'domain.ctera.local')
   folder_groups = admin.cloudfs.groups.all(user=bruce)

.. automethod:: cterasdk.core.cloudfs.FolderGroups.add
   :noindex:

.. code:: python

   """Create a Folder Group, owned by a local user account 'svc_account'"""
   svc_account = core_types.UserAccount('svc_account')
   admin.cloudfs.groups.add('FG-001', svc_account)

   """Create a Folder Group, owned by the domain user 'ctera.local\wbruce'"""
   wbruce = core_types.UserAccount('wbruce', 'ctera.local')
   admin.cloudfs.groups.add('FG-002', wbruce)

   admin.cloudfs.groups.add('FG-003') # without an owner

   """Create a Folder Group, assigned to an 'Archive' storage class"""
   admin.cloudfs.groups.add('Archive', core_types.UserAccount('svc_account'), storage_class='Archive')

.. automethod:: cterasdk.core.cloudfs.FolderGroups.modify
   :noindex:

.. code:: python

   """Rename a Folder Group"
   admin.cloudfs.groups.modify('FG-001', 'FG-002')

.. automethod:: cterasdk.core.cloudfs.FolderGroups.delete
   :noindex:

.. code:: python

   admin.cloudfs.groups.delete('FG-001')

Backup Folders
--------------

.. automethod:: cterasdk.core.cloudfs.Backups.all
   :noindex:

.. code:: python

   """List all backup folder"""
   for backup_folder in admin.cloudfs.backups.all():
      print(backup_folder)

.. automethod:: cterasdk.core.cloudfs.Backups.add
   :noindex:

.. code:: python

   """Create a backup folder"""
   folder_group = 'backup-fg'
   owner = core_types.UserAccount('bwayne', 'domain.ctera.local')
   admin.cloudfs.backups.add('my-backup', folder_group, owner)

.. automethod:: cterasdk.core.cloudfs.Backups.modify
   :noindex:

.. code:: python

   """Change backup folder owner"""
   bwayne = core_types.UserAccount('bwayne', 'domain.ctera.local')
   admin.cloudfs.backups.modify('my-backup', new_owner=bwayne)

.. automethod:: cterasdk.core.cloudfs.Backups.delete
   :noindex:

.. code:: python

   """Delete a backup folder"""
   admin.cloudfs.backups.modify('my-backup')

Cloud Drive Folders
-------------------

.. automethod:: cterasdk.core.cloudfs.CloudDrives.all
   :noindex:

.. code:: python

   """List all cloud drive folders"""
   cloud_drive_folders = admin.cloudfs.drives.all()
   for cloud_drive_folder in cloud_drive_folders:
       print(cloud_drive_folder)

   """List cloud drive folders owned by a domain user"""
   bruce = core_types.UserAccount('bruce', 'domain.ctera.local')
   cloud_drive_folders = admin.cloudfs.drives.all(user=bruce)

   """List both deleted and non-deleted cloud drive folders"""
   cloud_drive_folders = admin.cloudfs.drives.all(list_filter=core_enum.ListFilter.All)

   """List deleted cloud drive folders"""
   cloud_drive_folders = admin.cloudfs.drives.all(list_filter=core_enum.ListFilter.Deleted)

.. automethod:: cterasdk.core.cloudfs.CloudDrives.add
   :noindex:

.. code:: python

   """Create a Cloud Drive folder, owned by a local user account 'svc_account'"""
   svc_account = core_types.UserAccount('svc_account')
   admin.cloudfs.drives.add('DIR-001', 'FG-001', svc_account)
   admin.cloudfs.drives.add('DIR-003', 'FG-003', svc_account, winacls = False) # disable Windows ACL's
   admin.cloudfs.drives.add('DIR-003', 'FG-003', svc_account, quota = 1024) # Set folder quota, in GB

   """Create a Cloud Drive folder, owned by the domain user 'ctera.local\wbruce'"""
   wbruce = core_types.UserAccount('wbruce', 'ctera.local')
   admin.cloudfs.drives.add('DIR-002', 'FG-002', wbruce)

   """Create immutable Cloud Drive folders"""

   svc_account = core_types.UserAccount('svc_account')

   """
   Mode: Enterprise (i.e., allow privileged delete by the CTERA Compliance Officer role)
   Retention Period: 7 Years.
   Grace Period: 30 Minutes.
   """
   admin.cloudfs.groups.add('FG-Enterprise', svc_account)
   settings = core_types.ComplianceSettingsBuilder.enterprise(7, core_enum.Duration.Years).grace_period(30, core_enum.Duration.Minutes).build()
   admin.cloudfs.drives.add('Enterprise', 'FG-Enterprise', svc_account, compliance_settings=settings)

   """
   Mode: Compliance (data cannot be deleted after grace period expires)
   Retention Period: 1 Years.
   Grace Period: 1 Hour.
   """
   admin.cloudfs.groups.add('FG-Compliance', svc_account)
   settings = core_types.ComplianceSettingsBuilder.enterprise(1, core_enum.Duration.Years).grace_period(1, core_enum.Duration.Hours).build()
   admin.cloudfs.drives.add('Compliance', 'FG-Compliance', svc_account, compliance_settings=settings)

.. automethod:: cterasdk.core.cloudfs.CloudDrives.modify
   :noindex:

.. code:: python

   """Update Quota of a Cloud Drive Folder"""
   svc_account = core_types.UserAccount('svc_account')
   admin.cloudfs.drives.modify('DIR-001', svc_account, quota=5120) # Set folder quota to 5 TB

.. automethod:: cterasdk.core.cloudfs.CloudDrives.delete
   :noindex:

.. code:: python

   """Delete a Cloud Drive folder, owned by the local user account 'svc_account'"""
   svc_account = core_types.UserAccount('svc_account')
   admin.cloudfs.drives.delete('DIR-001', svc_account)

   """Delete a Cloud Drive folder permanently"""
   admin.cloudfs.drives.delete('DIR-001', svc_account, permanently=True)

   """Delete a Cloud Drive folder, owned by the domain user 'ctera.local\wbruce'"""
   wbruce = core_types.UserAccount('wbruce', 'ctera.local')
   admin.cloudfs.drives.delete('DIR-002', wbruce)

.. seealso:: Non-permanent deletion of Cloud Drive folders will transfer the Cloud Drive folder to the Trash Can.

.. automethod:: cterasdk.core.cloudfs.CloudDrives.recover
   :noindex:

.. code:: python

   """Recover a deleted Cloud Drive folder, owned by the local user account 'svc_account'"""
   svc_account = core_types.UserAccount('svc_account')
   admin.cloudfs.drives.recover('DIR-001', svc_account)

   """Recover a deleted Cloud Drive folder, owned by the domain user 'ctera.local\wbruce'"""
   wbruce = core_types.UserAccount('wbruce', 'ctera.local')
   admin.cloudfs.drives.recover('DIR-002', wbruce)

.. automethod:: cterasdk.core.cloudfs.CloudDrives.setfacl
   :noindex:

.. code:: python

   """Changing the file or Folder ACLs"""
   folders_paths = ["portaladmin/cloudFolder/diagrams", "adrian/data/docs"]
   sddl_string = 'O:S-1-12-1-1536910496-1126310805-1188065941-1612002142' \
                 'G:S-1-12-1-1536910496-1126310805-1188065941-1612002142' \
                 'D:AI(A;ID;FA;;;BA)(A;ID;FA;;;SY)(A;ID;0x1200a9;;;BU)(A;ID;0x1301bf;;;AU)'
   admin.cloudfs.drives.setfacl(folders_paths, sddl_string, True)

.. automethod:: cterasdk.core.cloudfs.CloudDrives.setoacl
   :noindex:

.. code:: python

   """Changing the File or Folder Owner SID or ACLs"""
   folders_paths = ["portaladmin/cloudFolder/diagrams", "dorian/data/docs"]
   owner_sid = 'S-1-12-1-1536910496-1126310805-1188065941-1612002142'
   admin.cloudfs.drives.setoacl(folders_paths, owner_sid, True)

Zones
-----

To manage zones, you must be a Read Write Administrator

.. automethod:: cterasdk.core.cloudfs.Zones.get
   :noindex:

.. code:: python

   zone = admin.cloudfs.zones.get('ZN-001')

.. automethod:: cterasdk.core.cloudfs.Zones.all
   :noindex:

.. code:: python

   for zone in admin.cloudfs.zones.all():
       print(zone)

.. automethod:: cterasdk.core.cloudfs.Zones.search
   :noindex:

.. code:: python

   for zone in admin.cloudfs.zones.search('ZN'):
       print(zone)

.. automethod:: cterasdk.core.cloudfs.Zones.add
   :noindex:

.. code:: python

   """
   Policy Types:
   - All: Include all cloud folders
   - Select: Select one or more cloud folders to include
   - None: Create an empty zone
   """

   """Create a zone with a description"""

   admin.cloudfs.zones.add('ZN-NYS-001', description = 'The New York State Zone')

   """Create a zone and include all folders"""

   admin.cloudfs.zones.add('ZN-NYS-002', 'All', 'All Folders')

   """Create an empty zone"""

   admin.cloudfs.zones.add('ZN-NYS-003', 'None', 'Empty Zone')

.. automethod:: cterasdk.core.cloudfs.Zones.add_folders
   :noindex:

.. code:: python

   """
   Add the following cloud folders to zone: 'ZN-001'

   1) 'Accounting' folder owned by 'Bruce'
   2) 'HR' folder owned by 'Diana'
   """

   accounting = core_types.CloudFSFolderFindingHelper('Accounting', 'Bruce')
   hr = core_types.CloudFSFolderFindingHelper('HR', 'Diana')

   admin.cloudfs.zones.add_folders('ZN-001', [accounting, hr])

.. automethod:: cterasdk.core.cloudfs.Zones.add_devices
   :noindex:

.. code:: python

   admin.cloudfs.zones.add_devices('ZN-001', ['vGateway-01ba', 'vGateway-bd02'])

.. automethod:: cterasdk.core.cloudfs.Zones.delete
   :noindex:

.. code:: python

   admin.cloudfs.zones.delete('ZN-001')

Timezone
========

.. automethod:: cterasdk.core.settings.GlobalSettings.get_timezone
   :noindex:

.. code:: python

   admin.settings.global_settings.get_timezone()

.. automethod:: cterasdk.core.settings.GlobalSettings.set_timezone
   :noindex:

.. code:: python

   admin.settings.global_settings.set_timzeone('(GMT-05:00) Eastern Time (US , Canada)')


Virtual Portal Settings
=======================

.. automethod:: cterasdk.core.settings.PortalSettings.get
   :noindex:

.. code:: python

   admin.settings.portal.get()

.. automethod:: cterasdk.core.settings.PortalSettings.use_global_settings
   :noindex:

.. automethod:: cterasdk.core.settings.PortalSettings.update
   :noindex:

.. code:: python

   settings = admin.settings.portal.get()
   settings.defaultMail = 'support@acme.com'  # assign default email to domain users without an email address
   admin.settings.portal.update(settings)  # apply settings changes


TLS Certificate
===============

.. automethod:: cterasdk.core.ssl.SSL.get
   :noindex:

.. code:: python

   certificate = admin.ssl.get()
   print(certificate)

.. automethod:: cterasdk.core.ssl.SSL.thumbprint
   :noindex:

.. code:: python

   print(admin.ssl.thumbprint)

.. automethod:: cterasdk.core.ssl.SSL.export
   :noindex:

.. code:: python

   admin.ssl.export()

   admin.ssl.export(r'C:\Temp')  # export to an alternate location

.. automethod:: cterasdk.core.ssl.SSL.import_from_zip
   :noindex:

.. code:: python

   admin.ssl.import_from_zip(r'C:\Users\jsmith\Downloads\certificate.zip')

.. automethod:: cterasdk.core.ssl.SSL.import_from_chain
   :noindex:

.. code:: python

   admin.ssl.import_from_chain(
       r'C:\Users\jsmith\Downloads\private.key',
       r'C:\Users\jsmith\Downloads\domain.crt',
       r'C:\Users\jsmith\Downloads\intermediate.crt',
       r'C:\Users\jsmith\Downloads\root.crt'
   )

Logging
=======

.. automethod:: cterasdk.core.logs.Logs.get
   :noindex:

.. automethod:: cterasdk.core.logs.Logs.device
   :noindex:

.. code:: python

   """Retrieve all cloud backup logs for device 'WIN-SRV2019'"""
   admin.logs.device('WIN-SRV2019', topic='backup')


Log Based Alerts
================

.. automethod:: cterasdk.core.logs.Alerts.get
   :noindex:

.. code:: python

   """Get a list of log based alerts"""
   for alert in admin.logs.alerts.get():
      print(alert)

.. automethod:: cterasdk.core.logs.Alerts.add
   :noindex:

.. code:: python

   """Alert on a volume full error event"""
   admin.logs.alerts.add('Volume Full', topic='system', log='VolumeFull', origin_type='Device', min_severity='error')

.. automethod:: cterasdk.core.logs.Alerts.put
   :noindex:

.. code:: python

   """Set alerts. Overrides all existing alerts"""
   volume_full = core_types.AlertBuilder.name('volume_full').log('VolumeFull').build()
   agent_repo = core_types.AlertBuilder.name('agent_repo').log('AgentRepositoryNotReady').build()
   admin.logs.alerts.put([volume_full, agent_repo])

.. automethod:: cterasdk.core.logs.Alerts.delete
   :noindex:

.. code:: python

   """Delete an alert by name"""
   admin.logs.alerts.delete('volume_full')

   """Delete all alerts"""
   admin.logs.alerts.put([])


Syslog
======

.. automethod:: cterasdk.core.syslog.Syslog.is_enabled
   :noindex:

.. automethod:: cterasdk.core.syslog.Syslog.get_configuration
   :noindex:

.. automethod:: cterasdk.core.syslog.Syslog.enable
   :noindex:

.. automethod:: cterasdk.core.syslog.Syslog.disable
   :noindex:


CLI Execution
=============

.. automethod:: cterasdk.core.cli.CLI.run_command
  :noindex:

.. code-block:: python

   result = admin.cli.run_command('show /settings')
   print(result)


Setup
=====

.. automethod:: cterasdk.core.setup.Setup.init_master
   :noindex:

.. code-block:: python

   admin.setup.init_master('admin', 'bruce.wayne@we.com', 'Bruce', 'Wayne', 'password1!', 'ctera.me')

.. automethod:: cterasdk.core.setup.Setup.init_application_server
   :noindex:

.. code-block:: python

   """Connect a secondary Portal server using a password"""
   master_ipaddr = '172.31.53.246'
   master_password = 'secret'
   admin.setup.init_application_server(master_ipaddr, master_password)

   """Connect a secondary Portal server using a private key"""
   master_ipaddr = '172.31.53.246'
   master_pk = """...PEM-encoded private key..."""
   admin.setup.init_application_server(master_ipaddr, master_pk)

.. automethod:: cterasdk.core.setup.Setup.init_replication_server
   :noindex:


Miscellaneous
=============

.. automethod:: cterasdk.objects.core.GlobalAdmin.test
   :noindex:

.. code-block:: python

   admin.test()

.. automethod:: cterasdk.objects.core.GlobalAdmin.whoami
   :noindex:

.. code-block:: python

   admin.whoami()
