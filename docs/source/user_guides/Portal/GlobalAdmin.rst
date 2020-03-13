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

   """Create an end user"""

   admin.users.add('bruce', 'bruce.wayne@we.com', 'Bruce', 'Wayne', 'G0th4amCity!')

.. automethod:: cterasdk.core.users.Users.delete
   :noindex:

.. code-block:: python

   """Delete a local user"""

   admin.users.delete('bruce')

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

   code = admin.activation.generate_code('bruce') # will look for 'bruce' in the current tenant

   code = admin.activation.generate_code('batman', 'gotham') # will look for 'bruce' in the gotham tenant

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

   admin.zones.add_folders('ZN-001', [('Accounting', 'Bruce'), ('HR', 'Diana')])

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

Create a Folder Group
^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.cloudfs.CloudFS.mkfg
   :noindex:

.. code:: python

   admin.cloudfs.mkfg('FG-001', 'svc_account')

   admin.cloudfs.mkfg('FG-002') # without an owner

Delete a Folder Group
^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.cloudfs.CloudFS.rmfg
   :noindex:

.. code:: python

   admin.cloudfs.rmfg('FG-002')

Create a Cloud Drive Folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.cloudfs.CloudFS.mkdir
   :noindex:

.. code:: python

   """Create a Cloud Drive folder, owned by a local user account 'svc_account'"""
   admin.cloudfs.mkdir('DIR-001', 'FG-001', ('local', 'svc_account'))

   """Create a Cloud Drive folder, owned by a domain user account 'wbruce'"""
   admin.cloudfs.mkdir('DIR-001', 'FG-001', ('ctera.local', 'wbruce'))

   admin.cloudfs.mkdir('DIR-002', 'FG-001', 'svc_account', winacls = False) # disable Windows ACL's

Delete a Cloud Drive Folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.cloudfs.CloudFS.delete
   :noindex:

.. code:: python

   admin.cloudfs.delete('DIR-001', 'svc_account')

Recover a Cloud Drive Folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automethod:: cterasdk.core.cloudfs.CloudFS.undelete
   :noindex:

.. code:: python

   admin.cloudfs.undelete('DIR-001', 'svc_account')
