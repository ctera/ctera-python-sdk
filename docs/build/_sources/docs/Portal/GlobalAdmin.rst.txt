*********************
Global Administration
*********************

.. contents:: Table of Contents

Instantiate a Global Admin object
---------------------------------

.. py:class:: GlobalAdmin(host[, port = 443][, https = True])

   :param host: The fully qualified domain name, hostname or an IPv4 address of the Gateway
   :param port: Set a custom port number (0 - 65535), defaults to ``443``
   :param https: Set to ``False`` to use HTTP, defaults to ``True``
   :type host: str
   :type port: int
   :type https: bool
   
.. code-block:: python

   admin = GlobalAdmin('chopin.ctera.com') # will use HTTPS over port 443
   
.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.http['ssl'] = 'Trust'``

Logging in
==========

.. py:method:: GlobalAdmin.test()

   Verification check to ensure the target host is a Portal.
   
.. code-block:: python

   admin.test()
   
.. py:method:: GlobalAdmin.login(username, password)

   Login to CTERA Portal as a Global Administrator.
   
   :param username: username
   :param password: password
   :type username: str
   :type password: str
   
.. code-block:: python

   admin.login('admin', 'G3neralZ0d!')

.. py:method:: GlobalAdmin.logout()

   Logout from CTERA Portal.
   
.. code-block:: python

   admin.logout()
   
.. py:method:: GlobalAdmin.whoami()

   Return the name of the logged in user.
   
   :returns: the name of the logged in user
   :rtype: str
   
.. code-block:: python

   admin.whoami()

Navigating
==========

.. py:method:: GlobalAdmin.browse_global_admin()

   Browse the Global Administration Portal.
   
   admin.browse_global_admin()

.. py:method:: GlobalAdmin.browse_tenant(name)

   :param name: a Virtual Portal name

   Browse a Team Portal.
   
.. code-block:: python

   admin.browse_tenant('chopin')
   
Core Methods
============

.. py:method:: GlobalAdmin.show(path)

   Print a Portal schema object as a JSON string.

.. py:method:: GlobalAdmin.show_multi(paths)

   Print one or more Portal schema objects as a JSON string.

.. py:method:: GlobalAdmin.get(path)
  
   Retrieve a Portal schema object as a Python object.

.. py:method:: GlobalAdmin.get_multi(path, paths)
 
   Retrieve one or more Portal schema objects as a Python object.

.. py:method:: GlobalAdmin.put(path, value)

   Update a Portal schema object or attribute.

.. py:method:: GlobalAdmin.execute(path, name[, param = None])

   Execute a Portal schema object method.

.. py:method:: GlobalAdmin.query(path, params, startFrom, countLimit)

.. py:method:: GlobalAdmin.show_query(path, params, startFrom, countLimit)

Portals
=======

Retrieve Portals
^^^^^^^^^^^^^^^^

.. py:method:: GlobalAdmin.tenants()

   Retrieve a list of Virtual Portals
   
   :returns: a list of virtual portals
   
.. code-block:: python

   for tenant in admin.tenants():
   
       print(tenant.name, tenant.usedStorageQuota, tenant.totalStorageQuota)

Create a Team Portal
^^^^^^^^^^^^^^^^^^^^

.. py:method:: GlobalAdmin.add_tenant(name[, display_name = None][, billing_id = None][, company = None])

   Create a Team Portal.

   :param name: name of the Team Portal
   :param display_name: display name
   :param billing_id: a billing id
   :param company: company
   :type name: str
   :type display_name: str
   :type billing_id: str
   :type company: str
   :returns: a relative url path to the Team Portal
   :rtype: str

.. code-block:: python
    
   """Create a Team Portal"""

   admin.add_tenant('acme')
   
   """Create a Team Portal, including a display name, billing id and a company name"""
   
   admin.add_tenant('ctera', 'CTERA', 'Tz9YRDSd8LNfaouzr3Db', 'CTERA Networks')
   
Delete a Team Portal
^^^^^^^^^^^^^^^^^^^^

.. py:method:: GlobalAdmin.delete_tenant(name)

   Delete a Team Portal.
   
   :param name: name of the Team Portal
   :type name: str
   
.. code-block:: python

   admin.delete_tenant('acme')
   
Recover a Team Portal
^^^^^^^^^^^^^^^^^^^^^
   
.. py:method:: GlobalAdmin.undelete_tenant(name)

   Recover a Team Portal.
   
   :param name: name of the Team Portal
   :type name: str
   
.. code-block:: python

   admin.undelete_tenant('acme')

Servers
=======

.. py:method:: GlobalAdmin.servers([include = ['name']])

   Retrieve the servers that comprise CTERA Portal.
   
   :param include: a list of attributes you wish to retrieve
   :type include: list
   :returns: a list of server objects
   :rtype: list
   
   To retrieve servers, you must first browse the Global Administration Portal, using: :py:func:`GlobalAdmin.browse_global_admin()`
   
.. code-block:: python

   """Retrieve all servers"""

   servers = admin.servers() # will only retrieve the server name
   
   for server in servers:

       print(server.name)
       
   """Retrieve multiple server attributes"""
       
   servers = admin.servers(include = ['name', 'connected', 'isApplicationServer', 'mainDB'])
   
   for server in servers:

       print(server)
   
Users
=====

Local Users
^^^^^^^^^^^

.. py:method:: GlobalAdmin.local_users([include = []])

   Retrieve local user accounts.

   :param include: a list of user attributes you wish to retrieve
   :type include: list[str]
   :returns: a list of user objects
   :rtype: list
   
   The `local_users` method will always retrieve the `name` attribute
   
.. code-block:: python

   users = admin.local_users()
   
   for user in users:

       print(user.name)
       
   users = admin.local_users(include = ['name', 'email', 'firstName', 'lastName'])
   
   for user in users:
   
       print(user)

.. py:method:: GlobalAdmin.add_user(username, email, first_name, last_name, password[, role = Role.EndUser][, company = None][, comment = None])

   Add a Portal user.

   :param username: username
   :param email: e-mail address
   :param first_name: first name
   :param last_name: last name
   :param password: password
   :param role: role
   :param company: company
   :param comment: comment
   :type username: str
   :type email: str
   :type first_name: str
   :type last_name: str
   :type password: str
   :type role: str
   :type company: str
   :type comment: str
   
.. code-block:: python

   """Create an end user"""

   admin.add_user('bruce', 'bruce.wayne@we.com', 'Bruce', 'Wayne', 'G0th4amCity!')
   
.. py:method:: GlobalAdmin.delete_user(username)

   Delete a Portal user.

   :param username: username
   :type username: str
   
.. code-block:: python

   """Delete a local user"""

   admin.delete_user('bruce')

Domain Users
^^^^^^^^^^^^

.. py:method:: GlobalAdmin.domains()

   Retrieve the list of Active Directory domains.
   
   :return: a list of fully qualified domain names
   :rtype: list

.. py:method:: GlobalAdmin.domain_users(domain[, include = []])

   Retrieve domain users.

   :param domain: the fully qualified domain name
   :param include: the list of user attributes you wish to retrieve
   :type domain: str
   :type include: list[str]
   :returns: a list of domain user objects
   :rtype: list
   
   The `domain_users` method will always include the `name` attribute
   
.. code-block:: python

   users = admin.domain_users('domain.ctera.local') # will only retrieve the 'name' attribute
   
   for user in users:

       print(user.name)
       
   """Retrieve additional user attributes"""
   
   users = admin.domain_users('domain.ctera.local', include = ['name', 'email', 'firstName', 'lastName'])
   
   print(user)

Fetch Users & Groups
^^^^^^^^^^^^^^^^^^^^

.. py:method:: GlobalAdmin.fetch(tuples)

   Fetch Active Directory domain users and groups.

   :param tuples: list of 3-tuple domain user or group entries
   :type include: list[tuple(str, str, str)]
   :returns: a path to a Portal background task
   :rtype: string
   
Devices
=======

.. py:method:: GlobalAdmin.device(name[, include = []])

   :param name: device name
   :param include: list of device attributes you wish to retrieve
   :type name: str
   :type include: list[str]
   :returns: a device object
   :rtype: ``Object``, :py:class:`Gateway` or :py:class:`Agent`

.. py:method:: GlobalAdmin.filers([include = []][, allPortals = False][, deviceTypes = None])

   :param include: list of Gateway attributes you wish to retrieve
   :param allPortals: whether to retrieve Gateways from all virtual portals, defaults to ``False``
   :param deviceTypes: list of Gateway device types, defaults to ``None``
   :type include: list[str]
   :type allPortals: bool
   :type deviceTypes: list[str]
   :returns: an interable list of :py:class:`Gateway` objects
   :rtype: list
   
   The `filers` method will always retrieve the following Gateway attributes: ``name``, ``deviceType``, ``portal``. You may use the `include` parameter to include additional attributes. To retrieve Gateways from all Portals, you must first browse the Global Administration Portal, using: :py:func:`GlobalAdmin.browse_global_admin()` and then set ``allPortals = True``. To filter specific device types, use the `deviceTypes` parameter as follows: ``deviceTypes = ['C200', 'C800P']``
   
.. code-block:: python

   """Retrieve all Gateways from the current tenant"""

   filers = admin.filers()
   
   for filer in filers:
   
       print(filer.name) # will print the Gateway name
   
   """Retrieve additional Gateway attributes"""
   
   filers = admin.filers(['owner', 'deviceConnectionStatus'])
   
   """Retrieve nested attributes using the '.' delimiter"""
   
   filers = admin.filers(['deviceReportedStatus.status.device.runningFirmware'])
   
   """Retrieve filers from all portals"""
   
   admin.browse_global_admin()
   
   filers = admin.filers(allPortals = True)
   
   """Retrieve C200's and C400's from all portals"""
   
   admin.browse_global_admin()
   
   filers = admin.filers(allPortals = True, deviceTypes = ['C200', 'C400'])
   
.. py:method:: GlobalAdmin.agents([include = []][, allPortals = False])

   :param include: list of Agent attributes you wish to retrieve
   :param allPortals: whether to retrieve Agents from all virtual portals, defaults to ``False``
   :type include: list[str]
   :type allPortals: bool
   :returns: an interable list of :py:class:`Agent` objects
   :rtype: list
   
   The `agents` method will always retrieve the following Agent attributes: ``name``, ``deviceType``, ``portal``. You may use the `include` parameter to include additional attributes. To retrieve Agents from all Portals, you must first browse the Global Administration Portal, using: :py:func:`GlobalAdmin.browse_global_admin()` and then set ``allPortals = True``. To filter specific device types, use the `deviceType` parameter as follows: ``deviceType = 'Server'`` or ``deviceType = 'Workstation'`` 
   
.. code-block:: python

   """Retrieve all Agents from the current tenant"""

   agents = admin.agents()
   
   for agent in agents:
   
       print(agent.name) # will print the Agent name
   
   """Retrieve all Agents and the underlying OS name"""
   
   agents = admin.agents(['deviceReportedStatus.status.agent.details.osName'])
   
.. py:method:: GlobalAdmin.server_agents([include = []][, allPortals = False])

   Retrieve server agents.
   
.. code-block:: python

   server_agents = admin.server_agents()
   
.. py:method:: GlobalAdmin.desktop_agents([include = []][, allPortals = False])

   Retrieve workstation agents.
   
.. code-block:: python

   desktop_agents = admin.desktop_agents()
   
.. py:method:: GlobalAdmin.devices_by_name(names[, include = []])

   Retrieve devices by name.
   
Generate Activation Codes
^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: GlobalAdmin.generate_code(user[, tenant = None])

   Generate a device activation code.
   
   :param user: user name
   :param tenant: a virtual portal name, defaults to ``None``
   :type user: str
   :type tenant: str
   
   This method will attempt to generate an activation code for user `user` in portal `portal`. 
   
.. code-block:: python

   """Generate a device activation code"""
   
   code = admin.generate_code('bruce') # will look for 'bruce' in the current tenant
   
   code = admin.generate_code('batman', 'gotham') # will look for 'bruce' in the gotham tenant
   
.. note:: Read Write Administrator, granted with the "Super User" role permission, can generate 200 codes every 5 minutes

generate_code(self, username, tenant = None)

Code Snippets
^^^^^^^^^^^^^

Generate activation codes for all domain users

.. code-block:: python

   # ... login ...

   users = admin.domain_users('dc.ctera.local') # obtain a list of domain users

   for user in users:

       activation_code = admin.generate_code(user.name) # generate activation code
       
       print((user.name, activation_code))
       
   # ... logout ...
   
Zones
-----

To manage zones, you must be a Read Write Administrator

Retrieving the Zones Class Object
=================================

.. code:: python

   admin = GlobalAdmin('chopin.ctera.com')
   
   admin.login('USERNAME', 'PASSWORD')
   
   zones = admin.zones() # returns a instance of Zones class object
   
Retrieve a Zone
^^^^^^^^^^^^^^^

.. py:method:: Zones.get(name)

   Retrieve a zone.
   
   :param name: zone name
   :type name: str

.. code:: python
   
   zone = zones.get('ZN-001')
   
Create a Zone
^^^^^^^^^^^^^
   
.. py:method:: Zones.add(name[, policy_type = 'Select'][, description = None])

   Create a zone.
   
   :param name: zone name
   :param policy_type: the policy type, defaults to ``'Select'``
   :param description: description
   :type name: str
   :type policy_type: str
   :type description: str

.. code:: python

   """
   Policy Types:
   - All: Include all cloud folders
   - Select: Select one or more cloud folders to include
   - None: Create an empty zone
   """

   """Create a zone with a description"""
   
   zones.add('ZN-NYS-001', description = 'The New York State Zone')
   
   """Create a zone and include all folders"""
   
   zones.add('ZN-NYS-002', 'All', 'All Folders')
   
   """Create an empty zone"""
   
   zones.add('ZN-NYS-003', 'None', 'Empty Zone')
   
Add Folders to a Zone
^^^^^^^^^^^^^^^^^^^^^
   
.. py:method:: Zones.add_folders(name, tuples)

   Add devices to a zone.
   
   :param name: zone name
   :param tuples: a list of 2-tuple cloud folder entries (folder, owner)
   :type name: str
   :type tuples: list(tuple(str, str), ...)

.. code:: python

   """
   Add the following cloud folders to zone: 'ZN-001'
   
   1) 'Accounting' folder owned by 'Bruce'
   2) 'HR' folder owned by 'Diana'
   
   """
   
   zones.add_folders('ZN-001', [('Accounting', 'Bruce'), ('HR', 'Diana')])
   
Add Devices to a Zone
^^^^^^^^^^^^^^^^^^^^^
   
.. py:method:: Zones.add_devices(name, devices)

   Add devices to a zone.
   
   :param name: zone name
   :param devices: a list of device names
   :type name: str
   :type devices: list(str)

.. code:: python
   
   zones.add_devices('ZN-001', ['vGateway-01ba', 'vGateway-bd02'])
   
Delete a Zone
^^^^^^^^^^^^^
   
.. py:method:: Zones.delete(name)

   Delete a zone.
   
   :param name: zone name
   :type name: str

.. code:: python
   
   zones.delete('ZN-001')

CloudFS
-------

To manage the Cloud File System, folder groups, backup and cloud drive folders, you must be a Read Write Administrator

Retrieving the CloudFS Class Object
===================================

.. code:: python

   admin = GlobalAdmin('chopin.ctera.com')
   
   admin.login('USERNAME', 'PASSWORD')
   
   cloudfs = admin.cloudfs() # returns a instance of CloudFS class object
   
Create a Folder Group
^^^^^^^^^^^^^^^^^^^^^

.. py:method:: CloudFS.mkfg(name[, user = None])

   Create a folder group.
   
   :param name: folder group name
   :param user: owner, defaults to ``None``
   :type name: str
   :type user: str

.. code:: python
   
   cloudfs.mkfg('FG-001', 'svc_account')
   
   cloudfs.mkfg('FG-002') # without an owner
   
Delete a Folder Group
^^^^^^^^^^^^^^^^^^^^^
   
.. py:method:: CloudFS.rmfg(name)

   Delete a folder group.
   
   :param name: folder group name
   :type name: str
   
.. code:: python
   
   cloudfs.rmfg('FG-002')
   
Create a Cloud Drive Folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
.. py:method:: CloudFS.mkdir(name, group, owner[, winacls = True])

   Create a cloud drive folder.
   
   :param name: cloud drive folder name
   :param group: folder group name
   :param user: user name (owner)
   :param winacls: enable Windows ACL's, defaults to ``True``
   :type name: str
   :type group: str
   :type user: str
   :type winacls: bool
   
.. code:: python
   
   cloudfs.mkdir('DIR-001', 'FG-001', 'svc_account')
   
   cloudfs.mkdir('DIR-002', 'FG-001', 'svc_account', winacls = False) # disable Windows ACL's
   
Delete a Cloud Drive Folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
.. py:method:: CloudFS.delete(name, owner)

   Delete a cloud drive folder.
   
   :param name: cloud drive folder name
   :param owner: user name
   :type name: str
   :type owner: str
   
.. code:: python
   
   cloudfs.delete('DIR-001', 'svc_account')
   
Recover a Cloud Drive Folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
.. py:method:: CloudFS.undelete(name, owner)

   Recover a deleted cloud drive folder.
   
   :param name: cloud drive folder name
   :param owner: user name
   :type name: str
   :type owner: str
   
.. code:: python
   
   cloudfs.undelete('DIR-001', 'svc_account')
   