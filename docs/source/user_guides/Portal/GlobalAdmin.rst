*********************
Global Administration
*********************

.. contents:: Table of Contents

Instantiate a Global Admin object
---------------------------------

.. autoclass:: cterasdk.object.Portal.GlobalAdmin
   :special-members: __init__
   :noindex:

.. code-block:: python

   admin = GlobalAdmin('chopin.ctera.com') # will use HTTPS over port 443

.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure this library to automatically trust the server's certificate, using: ``config.http['ssl'] = 'Trust'``

Setup
-----

.. automethod:: cterasdk.core.setup.Setup.init_master
   :noindex:

.. code-block:: python

   admin.init_master('admin', 'bruce.wayne@we.com', 'Bruce', 'Wayne', 'password1!', 'ctera.me')

.. automethod:: cterasdk.core.setup.Setup.init_application_server
   :noindex:

.. code-block:: python

   """Connect a secondary Portal server using a password"""
   master_ipaddr = '172.31.53.246'
   master_password = 'secret'
   admin.init_application_server(master_ipaddr, master_password)

   """Connect a secondary Portal server using a private key"""
   master_ipaddr = '172.31.53.246'
   master_pk = """...PEM-encoded private key..."""
   admin.init_application_server(master_ipaddr, master_pk)

.. automethod:: cterasdk.core.setup.Setup.init_replication_server
   :noindex:

Logging in
----------

.. automethod:: cterasdk.object.Portal.GlobalAdmin.test
   :noindex:

.. code-block:: python

   admin.test()

.. automethod:: cterasdk.object.Portal.GlobalAdmin.login
   :noindex:

.. code-block:: python

   admin.login('admin', 'G3neralZ0d!')

.. automethod:: cterasdk.object.Portal.GlobalAdmin.logout
   :noindex:

.. code-block:: python

   admin.logout()

.. automethod:: cterasdk.object.Portal.GlobalAdmin.whoami
   :noindex:

.. code-block:: python

   admin.whoami()

Navigating
----------

.. automethod:: cterasdk.core.portals.Portals.browse_global_admin
   :noindex:

.. code-block:: python

   admin.portals.browse_global_admin()

.. automethod:: cterasdk.core.portals.Portals.browse
   :noindex:

.. code-block:: python

   admin.portals.browse('chopin')

Core Methods
------------

.. automethod:: cterasdk.object.Portal.GlobalAdmin.show
   :noindex:
.. automethod:: cterasdk.object.Portal.GlobalAdmin.show_multi
   :noindex:
.. automethod:: cterasdk.object.Portal.GlobalAdmin.get
   :noindex:
.. automethod:: cterasdk.object.Portal.GlobalAdmin.put
   :noindex:
.. automethod:: cterasdk.object.Portal.GlobalAdmin.execute
   :noindex:
.. automethod:: cterasdk.object.Portal.GlobalAdmin.query
   :noindex:
.. automethod:: cterasdk.object.Portal.GlobalAdmin.show_query
   :noindex:

Storage Nodes
-------------
.. automethod:: cterasdk.core.buckets.Buckets.get
   :noindex:

.. code-block:: python

   bucket = filer.buckets.get('MainStorage')
   print(bucket)

   bucket = filer.buckets.get('MainStorage', include=['bucket', 'driver'])
   print(bucket.name, bucket.bucket, bucket.driver)

.. automethod:: cterasdk.core.buckets.Buckets.add
   :noindex:

.. code-block:: python

   """Add an Amazon S3 bucket called 'mybucket'"""
   bucket = portal_types.AmazonS3('mybucket', 'access-key', 'secret-key')
   filer.buckets.add('cterabucket', bucket)

   """Add an Amazon S3 bucket called 'mybucket', dedicated to a tenant called 'mytenant'"""
   bucket = portal_types.AmazonS3('mybucket', 'access-key', 'secret-key')
   filer.buckets.add('cterabucket', bucket, dedicated_to='mytenant')

   """Add a bucket in read-delete only mode"""
   bucket = portal_types.AmazonS3('mybucket', 'access-key', 'secret-key')
   filer.buckets.add('cterabucket', bucket, read_only=True)

.. automethod:: cterasdk.core.buckets.Buckets.modify
   :noindex:

.. code-block:: python

   """Modify an existing bucket, set it to read-delete only and dedicate it to 'mytenant'"""
   filer.buckets.modify('MainStorage', read_only=True, dedicated_to='mytenant')

.. automethod:: cterasdk.core.buckets.Buckets.list_buckets
   :noindex:

.. code-block:: python

   for bucket in filer.buckets.list_buckets():
       print(bucket)

.. automethod:: cterasdk.core.buckets.Buckets.delete
   :noindex:

.. code-block:: python

   filer.buckets.delete('MainStorage')

.. automethod:: cterasdk.core.buckets.Buckets.read_write
   :noindex:

.. code-block:: python

   filer.buckets.read_write('MainStorage')

.. automethod:: cterasdk.core.buckets.Buckets.read_only
   :noindex:

.. code-block:: python

   filer.buckets.read_only('MainStorage')


Portals
-------

Retrieve Portals
^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.portals.Portals.list_tenants
   :noindex:

.. code-block:: python

   """List all tenants"""
   for tenant in admin.portals.list_tenants():
       print(tenant)

   """List Team Portals. For each tenant, retrieve its creation date, subscription plan and activation status"""
   for tenant in admin.portals.list_tenants(include=['createDate', 'plan', 'activationStatus'], portal_type=portal_enum.PortalType.Team):
       print(tenant)

.. automethod:: cterasdk.core.portals.Portals.tenants
   :noindex:

.. code-block:: python

   for tenant in admin.portals.tenants():
       print(tenant.name, tenant.usedStorageQuota, tenant.totalStorageQuota)

Create a Team Portal
^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.portals.Portals.add
   :noindex:

.. code-block:: python

   """Create a Team Portal"""

   admin.portals.add('acme')

   """Create a Team Portal, including a display name, billing id and a company name"""

   admin.portals.add('ctera', 'CTERA', 'Tz9YRDSd8LNfaouzr3Db', 'CTERA Networks')

   """Create a Team Portal and assign it to a pre-configured subscription plan"""
   admin.portals.add('ctera', plan = 'Default')

Subscribe a Team Portal to a Plan
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.portals.Portals.delete
   :noindex:

.. code-block:: python

   admin.portals.delete_tenant('acme')

Recover a Team Portal
^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.portals.Portals.undelete
   :noindex:

.. code-block:: python

   admin.portals.undelete_tenant('acme')

Plans
-----
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
   Retention Policy (portal_enum.PlanRetention):
   - All: All Versions
   - Hourly: Hourly Versions
   - Daily: Daily Versions
   - Weekly: Weekly Versions
   - Monthly: Monthly Versions
   - Quarterly: Quarterly Versions
   - Yearly: Yearly Versions
   - Deleted: Recycle Bin

   Quotas (portal_enum.PlanItem):
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
   retention = {portal_enum.PlanRetention.Daily: 7, portal_enum.PlanRetention.Monthly: 12}
   quotas = {portal_enum.PlanItem.EV16: 10, portal_enum.PlanItem.EV32: 5, portal_enum.PlanItem.Share: 100}
   admin.plans.add(name, retention, quotas)

.. automethod:: cterasdk.core.plans.Plans.modify
   :noindex:

.. code-block:: python

   """
   Modify 'good_plan' subscription plan:
   1) Retention: 30 daily versions, 36 monthly versions
   2) Quotas: 20 x EV16, 10 x EV32, 200 x Cloud Drive (Share)
   """

   name = 'good_plan'
   retention = {portal_enum.PlanRetention.Daily: 30, portal_enum.PlanRetention.Monthly: 36}
   quotas = {portal_enum.PlanItem.EV16: 20, portal_enum.PlanItem.EV32: 10, portal_enum.PlanItem.Share: 200}
   admin.plans.modify(name, retention, quotas)

.. automethod:: cterasdk.core.plans.Plans.delete
   :noindex:

.. code-block:: python

   name = 'good_plan'
   admin.plan.delete(name)

Plan Auto Assignment Rules
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.core.plans.PlanAutoAssignPolicy.get_policy
   :noindex:

.. automethod:: cterasdk.core.plans.PlanAutoAssignPolicy.set_policy
   :noindex:

.. code-block:: python

   """Apply the '100GB' plan to all user names that start with 'adm'"""
   c1 = portal_types.PlanCriteriaBuilder.username().startswith('adm').build()
   r1 = PolicyRule('100GB', c1)

   """Apply the '200GB' plan to all user names that end with 'inc'"""
   c2 = portal_types.PlanCriteriaBuilder.username().endswith('inc').build()
   r2 = PolicyRule('200GB', c2)

   """Apply the 'Bingo' plan to all user names that contain 'bing'"""
   c3 = portal_types.PlanCriteriaBuilder.username().contains('bing').build()
   r3 = PolicyRule('Bingo', c3)

   """Apply the 'ABC' plan to 'alice', 'bob' and 'charlie'"""
   c4 = portal_types.PlanCriteriaBuilder.username().isoneof(['alice', 'bob', 'charlie']).build()
   r4 = PolicyRule('ABC', c4)

   """Apply the '10TB' plan to read write, read only and support administrators"""
   roles = [portal_enum.Role.ReadWriteAdmin, portal_enum.Role.ReadOnlyAdmin, portal_enum.Role.Support]
   c5 = portal_types.PlanCriteriaBuilder.role().include(roles).build()
   r5 = PolicyRule('10TB', c5)

   """Apply the 'TechStaff' plan to the 'Product' and 'Support' groups"""
   c6 = portal_types.PlanCriteriaBuilder.user_groups().include(['Product', 'Support']).build()
   r6 = PolicyRule('TechStaff', c6)

   admin.plans.auto_assign.set_policy([r1, r2, r3, r4, r5, r6])

   """Remove all policy rules"""
   admin.plans.auto_assign.set_policy([])

   """Do not assign a default plan if no match applies"""
   admin.plans.auto_assign.set_policy([], False)

   """Assign 'Default' if no match applies"""
   admin.plans.auto_assign.set_policy([], True, 'Default')

Configuration Templates
-----------------------

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
   #. Enumerator containing a list of platforms. c:py:class:`cterasdk.core.enum.Platform`

.. code-block:: python

   """Include all 'pptx', 'xlsx' and 'docx' file types for all users"""
   docs = common_types.FileFilterBuilder.extensions().include(['pptx', 'xlsx', 'docx']).build()
   include_sets = common_types.FilterBackupSet('Documents', filter_rules=[docs],
                                                         template_dirs=[portal_enum.EnvironmentVariables.ALLUSERSPROFILE])

   """Exclude all 'cmd', 'exe' and 'bat' file types for all users"""
   programs = common_types.FileFilterBuilder.extensions().include(['cmd', 'exe', 'bat']).build()
   exclude_sets = common_types.FilterBackupSet('Programs', filter_rules=[programs],
                                                           template_dirs=[portal_enum.EnvironmentVariables.ALLUSERSPROFILE])

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
   versions = [portal_types.PlatformVersion(portal_enum.Platform.Edge_7, '7.0.981.7')]  # use 7.0.981.7 for v7 Edge Filers

   admin.templates.add('MyTemplate', 'woohoo', include_sets=[include_sets], exclude_sets=[exclude_sets],
                       backup_schedule=backup_schedule, apps=apps, versions=versions)

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: cterasdk.core.templates.TemplateAutoAssignPolicy.get_policy
   :noindex:

.. automethod:: cterasdk.core.templates.TemplateAutoAssignPolicy.set_policy
   :noindex:

.. code-block:: python

   """Apply the 'ESeries' template to devices of type: C200, C400, C800, C800P"""
   device_types = [portal_enum.DeviceType.C200, portal_enum.DeviceType.C400, portal_enum.DeviceType.C800, portal_enum.DeviceType.C800P]
   c1 = portal_types.TemplateCriteriaBuilder.type().include(device_types).build()
   r1 = PolicyRule('ESeries', c1)

   """Apply the 'Windows' template to devices that use a 'Windows' operating system"""
   c2 = portal_types.TemplateCriteriaBuilder.os().contains('Windows').build()
   r2 = PolicyRule('Windows', c2)

   """Apply the 'CTERA7' template to devices running version 7"""
   c3 = portal_types.TemplateCriteriaBuilder.version().startswith('7.0').build()
   r3 = PolicyRule('CTERA7', c3)

   """Apply the 'WD5' template to devices that their hostname ends with 'WD5'"""
   c4 = portal_types.TemplateCriteriaBuilder.hostname().endswith('WD5').build()
   r4 = PolicyRule('WD5', c4)

   """Apply the 'Beta' template to devices that their name is one of"""
   c5 = portal_types.TemplateCriteriaBuilder.name().isoneof(['DEV1', 'DEV2', 'DEV3']).build()
   r5 = PolicyRule('Beta', c5)

   admin.templates.auto_assign.set_policy([r1, r2, r3, r4, r5])

   """Remove all policy rules"""
   admin.templates.auto_assign.set_policy([])

   """Do not assign a default template if no match applies"""
   admin.templates.auto_assign.set_policy([], False)

   """Assign 'Default' if no match applies"""
   admin.templates.auto_assign.set_policy([], True, 'Default')

Servers
-------
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

Antivirus
---------

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
^^^^^^^^^^^^^^^^^

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

Users
-----

.. automethod:: cterasdk.core.users.Users.delete
   :noindex:

.. code-block:: python

   """Delete a local user"""

   alice = portal_types.UserAccount('alice')
   admin.users.delete(alice)

   """Delete a domain user"""

   bruce = portal_types.UserAccount('bruce', 'domain.ctera.local')
   admin.users.delete(bruce)

Local Users
^^^^^^^^^^^
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
^^^^^^^^^^^^

.. automethod:: cterasdk.core.users.Users.list_domains
   :noindex:
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

   alice = portal_types.UserAccount('alice', 'domain.ctera.local')
   bruce = portal_types.UserAccount('bruce', 'domain.ctera.local')

   admin.directoryservice.fetch([alice, bruce])

Directory Services
------------------
.. automethod:: cterasdk.core.directoryservice.DirectoryService.connect
   :noindex:

.. code-block:: python

   """Connect to Active Directory using a primary domain controller, configure domain UID/GID mapping and access control"""
   mapping = [portal_types.ADDomainIDMapping('demo.local', 200001, 5000000), portal_types.ADDomainIDMapping('trusted.local', 5000001, 10000000)]
   rw_admin_group = portal_types.AccessControlEntry(
       portal_types.GroupAccount('ctera_admins', 'demo.local'),
       portal_enum.Role.ReadWriteAdmin
   )
   ro_admin_user = portal_types.AccessControlEntry(
       portal_types.UserAccount('jsmith', 'demo.local'),
       portal_enum.Role.ReadOnlyAdmin
   )
   admin.directoryservice.connect('demo.local', 'svc_account', 'P@ssw0rd1', mapping=mapping, domain_controllers=portal_types.DomainControllers('172.54.3.52'), acl=[rw_admin, ro_admin])

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
   mapping = [portal_types.ADDomainIDMapping('demo.local', 200001, 5000000), portal_types.ADDomainIDMapping('trusted.local', 5000001, 10000000)]
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
   rw_admin_group = portal_types.AccessControlEntry(
       portal_types.GroupAccount('ctera_admins', 'demo.local'),
       portal_enum.Role.ReadWriteAdmin
   )
   ro_admin_user = portal_types.AccessControlEntry(
       portal_types.UserAccount('jsmith', 'demo.local'),
       portal_enum.Role.ReadOnlyAdmin
   )
   admin.directoryservice.set_access_control([rw_admin_group, ro_admin_user], portal_enum.Role.Disabled)

.. automethod:: cterasdk.core.directoryservice.DirectoryService.disconnect
   :noindex:

.. code-block:: python

   admin.directoryservice.disconnect()

Devices
-------
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

   server_agents = admin.devices.server()

.. automethod:: cterasdk.core.devices.Devices.desktops
   :noindex:

.. code-block:: python

   desktop_agents = admin.devices.desktop_agents()

.. automethod:: cterasdk.core.devices.Devices.by_name
   :noindex:

Generate Activation Codes
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.activation.Activation.generate_code
   :noindex:

.. code-block:: python

   """Generate a device activation code"""

   code = admin.activation.generate_code() # will generate a code for the current, logged on, user

   code = admin.activation.generate_code('bruce') # will generate a code for 'bruce' in the current tenant

   code = admin.activation.generate_code('batman', 'gotham') # will generate a code for 'bruce' in the 'gotham' tenant

.. note:: Read Write Administrator, granted with the "Super User" role permission, can generate 200 codes every 5 minutes

Code Snippets
^^^^^^^^^^^^^

Generate activation codes for all domain users

.. code-block:: python

   # ... login ...

   users = admin.users.list_domain_users('dc.ctera.local') # obtain a list of domain users

   for user in users:

       activation_code = admin.activation.generate_code(user.name) # generate activation code

       print((user.name, activation_code))

   # ... logout ...

Zones
-----

To manage zones, you must be a Read Write Administrator

Retrieve a Zone
^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.zones.Zones.get
   :noindex:

.. code:: python

   zone = admin.zones.get('ZN-001')

Create a Zone
^^^^^^^^^^^^^
.. automethod:: cterasdk.core.zones.Zones.add
   :noindex:

.. code:: python

   """
   Policy Types:
   - All: Include all cloud folders
   - Select: Select one or more cloud folders to include
   - None: Create an empty zone
   """

   """Create a zone with a description"""

   admin.zones.add('ZN-NYS-001', description = 'The New York State Zone')

   """Create a zone and include all folders"""

   admin.zones.add('ZN-NYS-002', 'All', 'All Folders')

   """Create an empty zone"""

   admin.zones.add('ZN-NYS-003', 'None', 'Empty Zone')

Add Folders to a Zone
^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.zones.Zones.add_folders
   :noindex:

.. code:: python

   """
   Add the following cloud folders to zone: 'ZN-001'

   1) 'Accounting' folder owned by 'Bruce'
   2) 'HR' folder owned by 'Diana'
   """

   accounting = portal_types.CloudFSFolderFindingHelper('Accounting', 'Bruce')
   hr = portal_types.CloudFSFolderFindingHelper('HR', 'Diana')

   admin.zones.add_folders('ZN-001', [accounting, hr])

Add Devices to a Zone
^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.zones.Zones.add_devices
   :noindex:

.. code:: python

   admin.zones.add_devices('ZN-001', ['vGateway-01ba', 'vGateway-bd02'])

Delete a Zone
^^^^^^^^^^^^^
.. automethod:: cterasdk.core.zones.Zones.delete
   :noindex:

.. code:: python

   admin.zones.delete('ZN-001')

CloudFS
-------

To manage the Cloud File System, folder groups, backup and cloud drive folders,
you must be a Read Write Administrator

Folder Groups
^^^^^^^^^^^^^
.. automethod:: cterasdk.core.cloudfs.CloudFS.list_folder_groups
   :noindex:

.. code:: python

   """List all folder groups"""
   folder_groups = admin.cloudfs.list_folder_groups()
   for folder_group in folder_groups:
       print(folder_group.name, folder_group.owner)

   """List folder groups owned by a domain user"""
   bruce = portal_types.UserAccount('bruce', 'domain.ctera.local')
   folder_groups = admin.cloudfs.list_folder_groups(user=bruce)

.. automethod:: cterasdk.core.cloudfs.CloudFS.mkfg
   :noindex:

.. code:: python

   """Create a Folder Group, owned by a local user account 'svc_account'"""
   svc_account = portal_types.UserAccount('svc_account')
   admin.cloudfs.mkfg('FG-001', svc_account)

   """Create a Folder Group, owned by the domain user 'ctera.local\wbruce'"""
   wbruce = portal_types.UserAccount('wbruce', 'ctera.local')
   admin.cloudfs.mkfg('FG-002', wbruce)

   admin.cloudfs.mkfg('FG-003') # without an owner

.. automethod:: cterasdk.core.cloudfs.CloudFS.rmfg
   :noindex:

.. code:: python

   admin.cloudfs.rmfg('FG-001')

Cloud Drive Folders
^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.cloudfs.CloudFS.list_folders
   :noindex:

.. code:: python

   """List all cloud drive folders"""
   cloud_drive_folders = admin.cloudfs.list_folders()
   for cloud_drive_folder in cloud_drive_folders:
       print(cloud_drive_folder)

   """List cloud drive folders owned by a domain user"""
   bruce = portal_types.UserAccount('bruce', 'domain.ctera.local')
   cloud_drive_folders = admin.cloudfs.list_folders(user=bruce)

   """List both deleted and non-deleted cloud drive folders"""
   cloud_drive_folders = admin.cloudfs.list_folders(list_filter=portal_enum.ListFilter.All)

   """List deleted cloud drive folders"""
   cloud_drive_folders = admin.cloudfs.list_folders(list_filter=portal_enum.ListFilter.Deleted)

.. automethod:: cterasdk.core.cloudfs.CloudFS.mkdir
   :noindex:

.. code:: python

   """Create a Cloud Drive folder, owned by a local user account 'svc_account'"""
   svc_account = portal_types.UserAccount('svc_account')
   admin.cloudfs.mkdir('DIR-001', 'FG-001', svc_account)
   admin.cloudfs.mkdir('DIR-003', 'FG-003', svc_account, winacls = False) # disable Windows ACL's

   """Create a Cloud Drive folder, owned by the domain user 'ctera.local\wbruce'"""
   wbruce = portal_types.UserAccount('wbruce', 'ctera.local')
   admin.cloudfs.mkdir('DIR-002', 'FG-002', wbruce)

.. automethod:: cterasdk.core.cloudfs.CloudFS.delete
   :noindex:

.. code:: python

   """Delete a Cloud Drive folder, owned by the local user account 'svc_account'"""
   svc_account = portal_types.UserAccount('svc_account')
   admin.cloudfs.delete('DIR-001', svc_account)

   """Delete a Cloud Drive folder, owned by the domain user 'ctera.local\wbruce'"""
   wbruce = portal_types.UserAccount('wbruce', 'ctera.local')
   admin.cloudfs.delete('DIR-002', wbruce)

.. automethod:: cterasdk.core.cloudfs.CloudFS.undelete
   :noindex:

.. code:: python

   """Recover a deleted Cloud Drive folder, owned by the local user account 'svc_account'"""
   svc_account = portal_types.UserAccount('svc_account')
   admin.cloudfs.undelete('DIR-001', svc_account)

   """Recover a deleted Cloud Drive folder, owned by the domain user 'ctera.local\wbruce'"""
   wbruce = portal_types.UserAccount('wbruce', 'ctera.local')
   admin.cloudfs.undelete('DIR-002', wbruce)

Timezone
--------

.. automethod:: cterasdk.core.settings.GlobalSettings.get_timezone
   :noindex:

.. code:: python

   admin.settings.global_settings.get_timezone()

.. automethod:: cterasdk.core.settings.GlobalSettings.set_timezone
   :noindex:

.. code:: python

   admin.settings.global_settings.set_timzeone('(GMT-05:00) Eastern Time (US , Canada)')

SSL Certificate
---------------

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

Logs
----

.. automethod:: cterasdk.core.logs.Logs.get
   :noindex:

.. automethod:: cterasdk.core.logs.Logs.device
   :noindex:

.. code:: python

   """Retrieve all cloud backup logs for device 'WIN-SRV2019'"""
   admin.logs.device('WIN-SRV2019', topic='backup')


Syslog
------

.. automethod:: cterasdk.core.syslog.Syslog.enable
   :noindex:

.. automethod:: cterasdk.core.syslog.Syslog.disable
   :noindex:
