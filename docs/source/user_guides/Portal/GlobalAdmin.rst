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

.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.http['ssl'] = 'Trust'``

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

   admin.portals.apply_changes()
   admin.portals.apply_changes(wait=True)  # wait for all changes to apply

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

Servers
-------
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
