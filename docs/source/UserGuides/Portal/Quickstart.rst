==========
Quickstart
==========

Eager to get started? This page gives a good introduction in how to get started with the CTERA SDK and the Portal APIs.

First, make sure that cterasdk is :ref:`installed<cterasdk-installation>` and up-to-date

Let’s get started with some simple examples.

Logging In
----------
Begin by importing the cterasdk module:

.. code-block:: python

    import cterasdk.settings
    from cterasdk import GlobalAdmin, ServicesPortal

Now, let's login to CTERA Portal as a global admin:

.. code-block:: python

    from cterasdk import GlobalAdmin

    def main():

        with GlobalAdmin('tenant.ctera.com') as admin:
            admin.login('admin-username', 'admin-password')  # equivalent to logging in to '/admin'

    if __name__ == '__main__':
        main()

Alternatively, we can also login to CTERA Portal as a Team Portal (tenant) user or admin.

.. code-block:: python

    from cterasdk import ServicesPortal

    def main():

        with ServicesPortal('tenant.ctera.com') as user:
            user.login('username', 'password')  # equivalent to logging in to '/ServicesPortal'

    if __name__ == '__main__':
        main()

.. note:: To ignore SSL errors, or log in using an IP address, use: ``cterasdk.settings.sessions.management.ssl = False``

Now we have an authenticated ``admin`` or ``user`` session. We can now proceed to access the Portal API's.

.. code-block:: python

    """As a global admin, we can list all tenants"""
    for tenant in admin.portals.list_tenants():
        print(tenant)

    """Let us assume we have a tenant called: 'acme'. We can navigate to this tenant"""
    admin.portals.browse('acme')

    """List all the Cloud Drive folders in the 'acme' tenant, their size and file count"""
    for drive in admin.cloudfs.drives.all(include=['folderStats']):
        print('Name: ', drive.name)
        print('Size: ', drive.folderStats.cloudFolderSize)
        print('Count: ', drive.folderStats.totalFiles)

    """List all the Edge Filers connected to the 'acme' tenant and their connection status"""
    for edge in admin.devices.filers(include=['deviceConnectionstatus']):
        print(edge)

    """To return to the Global Administration"""
    admin.portals.browse_global_admin()

If we combine the two examples above, we get the following result:

.. code-block:: python

    from cterasdk import GlobalAdmin

    def main():
        with GlobalAdmin('tenant.ctera.com') as admin:
            admin.login('admin-username', 'admin-password')
            for tenant in admin.portals.list_tenants():
                print(tenant)

            admin.portals.browse('acme')

            for drive in admin.cloudfs.drives.all(include=['folderStats']):
                print('Name: ', drive.name)
                print('Size: ', drive.folderStats.cloudFolderSize)
                print('Count: ', drive.folderStats.totalFiles)

            for edge in admin.devices.filers(include=['deviceConnectionstatus']):
                print(edge)

            admin.portals.browse_global_admin()

    if __name__ == '__main__':
        main()

A context manager is not mandatory but ``admin.logout()`` should be called in this case.
And equivalnent example to the one given above:

.. code-block:: python

    import cterasdk.settings
    from cterasdk import Edge

    from cterasdk import GlobalAdmin

    def main():

        admin = GlobalAdmin('tenant.ctera.com')
        admin.login('admin-username', 'admin-password')
        for tenant in admin.portals.list_tenants():
            print(tenant)

        admin.portals.browse('acme')

        for drive in admin.cloudfs.drives.all(include=['folderStats']):
            print('Name: ', drive.name)
            print('Size: ', drive.folderStats.cloudFolderSize)
            print('Count: ', drive.folderStats.totalFiles)

        for edge in admin.devices.filers(include=['deviceConnectionstatus']):
            print(edge)

        admin.portals.browse_global_admin()
        admin.logout()

    if __name__ == '__main__':
        main()


Management API
--------------
The ``GlobalAdmin`` and ``ServicesPortal`` objects feature an ``api`` property used for accessing *Core Methods* of the Portal API.

.. warning:: For optimal integration, it's advised to utilize the modules provided in this SDK instead of the ``api`` property. In cases where a specific command or module is absent, `please submit a feature request <https://github.com/ctera/ctera-python-sdk/issues>`_.

.. automethod:: cterasdk.clients.synchronous.clients.API.get
   :noindex:

.. automethod:: cterasdk.clients.synchronous.clients.API.get_multi
   :noindex:

.. automethod:: cterasdk.clients.synchronous.clients.API.put
   :noindex:

.. automethod:: cterasdk.clients.synchronous.clients.API.add
   :noindex:

.. automethod:: cterasdk.clients.synchronous.clients.API.execute
   :noindex:

.. automethod:: cterasdk.clients.synchronous.clients.API.delete
   :noindex:

Data Types and Enumerators
--------------------------
Certain modules require input parameters comprising of complex data types or values selected from predefined lists.
Complex data types are available in ``core_types`` module, while ``core_enum`` offers a comprehensive list of options for closed selection.
In the following example, we represent the compliance settings of a Cloud Drive Folder ``core_types`` and ``core_enum`` modules.
The compliance settings are then used to create a cloud drive folder.

.. code-block:: python

    from cterasdk import core_types, core_enum

    admin.cloudfs.groups.add('FG-Compliance', svc_account)  # Create a folder-group
    settings = core_types.ComplianceSettingsBuilder.enterprise(1, core_enum.Duration.Years).grace_period(1, core_enum.Duration.Hours).build()
    admin.cloudfs.drives.add('Compliance', 'FG-Compliance', svc_account, compliance_settings=settings)

Complex types and predefined lists that are shared across CTERA Drive, Edge, and Portal are in ``common_types`` and ``common_enum``.

File Access
-----------
The SDK features a file browser module for managing files.

.. code-block:: python

    user.files.mkdir('The/quick/brown/fox')  # Creates the dir 'fox' in the following path: 'The/quick/brown'
    user.files.makedirs('The/quick/brown/fox')  # Creates the entire directory path recursively
    user.files.copy(*['My Files/Documents/Sample.docx', 'My Files/Documents/Burndown.xlsx'], destination='The/quick/brown/fox')
    user.files.move(*['My Files/Documents/Sample.docx', 'My Files/Documents/Wizard Of Oz.docx'], destination='The/quick/brown/fox')
    user.files.delete('The/quick/brown/fox/document.docx')
    user.files.download('The/quick/brown/fox/document.docx')
    user.files.download_as_zip('The/quick/brown/fox', ['document.docx', 'chart.xlsx', 'deck.pptx'])

Remote Access to CTERA Edge and Drive
-------------------------------------
You can invoke the CTERA Edge and Drive API's through CTERA Portal.

.. code-block:: python

    with GlobalAdmin('tenant.ctera.com') as admin:
        admin.login('admin-username', 'admin-password')
        edge_filers = admin.devices.filers()
        for edge in edge_filers:
            print(edge.config.get_hostname())

By default, the Portal provides limited access to the Edge and Drive API. To access the full set of APIs, use the ``remote_access`` command.

.. code-block:: python

    with GlobalAdmin('tenant.ctera.com') as admin:
        admin.login('admin-username', 'admin-password')
        edge_filers = admin.devices.filers()
        for edge in edge_filers:
            remote_session = edge.remote_access()
            print(remote_access.ctera_migrate.list_tasks())  # List migration tasks
