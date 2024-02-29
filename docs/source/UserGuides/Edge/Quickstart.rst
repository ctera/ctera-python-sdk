==========
Quickstart
==========

Eager to get started? This page gives a good introduction in how to get started with the CTERA SDK and the Edge Filer APIs.

First, make sure that aiohttp is :ref:`installed<cterasdk-installation>` and up-to-date

Let’s get started with some simple examples.

Logging In
----------
Begin by importing the cterasdk module:

.. code-block:: python

    import cterasdk.settings
    from cterasdk import Edge

Now, let's login to the CTERA Edge Filer:

.. code-block:: python

    import cterasdk.settings
    from cterasdk import Edge

    def main():

        """By default, the Edge Filer uses a self-signed certificate.
        Therefore, we have to disable TLS/SSL verification to successfully login for the first time.
        """
        cterasdk.settings.sessions.management.ssl = False  # disables TLS verification
        with Edge('192.168.0.1') as edge:
            edge.login('admin-username', 'admin-password')

    if __name__ == '__main__':
        main()

.. note:: to ignore SSL errors, or log in using an IP address, use: ``cterasdk.settings.sessions.management.ssl = False``

Now we have an authenticated ``edge`` session. We can now proceed to access the Edge Filer API's.

.. code-block:: python

    edge.config.set_hostname('edge-filesystem')
    edge.volumes.add('data')  # create a volume called 'data'
    edge.services.connect('tenant.ctera.com', 'portal-usern', 'portal-user-pass')  # connect to the Portal
    edge.cache.enable()  # enable caching
    
    for share in edge.shares.get():  # get all shares
        print(share.name)  # print share name

If we combine the two examples above, we get the following result:

.. code-block:: python

    import cterasdk.settings
    from cterasdk import Edge

    def main():

        """By default, the Edge Filer uses a self-signed certificate.
        Therefore, we have to disable TLS/SSL verification to successfully login for the first time.
        """
        cterasdk.settings.sessions.management.ssl = False
        with Edge('192.168.0.1') as edge:
            edge.login('admin-username', 'admin-password')
            edge.config.set_hostname('edge-filesystem')
            edge.volumes.add('data')
            edge.services.connect('tenant.ctera.com', 'portal-user', 'portal-user-pass')
            edge.cache.enable()
            
            for share in edge.shares.get():
                print(share.name)

    if __name__ == '__main__':
        main()

A context manager is not mandatory but ``edge.logout()`` should be called in this case.
And equivalnent example to the one given above:

.. code-block:: python

    import cterasdk.settings
    from cterasdk import Edge

    def main():

        """By default, the Edge Filer uses a self-signed certificate.
        Therefore, we have to disable TLS/SSL verification to successfully login for the first time.
        """
        cterasdk.settings.sessions.management.ssl = False
        edge = Edge('192.168.0.1')

        edge.login('admin-username', 'admin-password')
        edge.config.set_hostname('edge-filesystem')
        edge.volumes.add('data')
        edge.services.connect('tenant.ctera.com', 'portal-user', 'portal-user-pass')
        edge.cache.enable()
        
        for share in edge.shares.get():
            print(share.name)
        
        edge.logout() # logout -- mandatory

    if __name__ == '__main__':
        main()


Management API
--------------
The ``Edge`` object features an ``api`` property used for accessing *Core Methods* of the Edge Filer API.

.. warning:: For optimal integration, it's advised to utilize the modules provided in this SDK instead of the ``api`` property. In cases where a specific command or module is absent, `please submit a feature request <https://github.com/ctera/ctera-python-sdk/issues>`_.

.. automethod:: cterasdk.aio_client.clients.API.get
   :noindex:

.. code-block:: python

    hostname = edge.api.get('/config/device/hostname')  # Not recommended
    hostname = edge.config.get_hostname()  # Recommended: using the config module and the get_hostname() command

.. automethod:: cterasdk.aio_client.clients.API.get_multi
   :noindex:

.. automethod:: cterasdk.aio_client.clients.API.put
   :noindex:

.. code-block:: python

    hostname = edge.api.put('/config/device/hostname', 'edge-filesystem')  # Not recommended
    hostname = edge.config.set_hostname('edge-filesystem')  # Recommended: using the config module and the set_hostname() command

.. automethod:: cterasdk.aio_client.clients.API.add
   :noindex:

.. code-block:: python

    from cterasdk import Object

    """Not recommended way of adding a local user to an Edge Filer"""
    user = Object()
    user.username = 'alice'
    user.password = 'secret-password'
    user.fullName = 'Alice Wonderland'
    user.email = 'alice.wonderland@acme.com'
    user.uid = 501
    edge.api.add('/config/auth/users', user)

    """Recommended way of adding a local user"""
    edge.users.add('alice', 'secret-password', 'Alice Wonderland', 'alice.wonderland@acme.com', 501)

.. automethod:: cterasdk.aio_client.clients.API.execute
   :noindex:

.. code-block:: python

   edge.api.execute('/config/cloudsync', 'forceExecuteEvictor')  # Not recommended: Start the cache eviction process (force)
   edge.cache.force_eviction()  # Recommended

.. automethod:: cterasdk.aio_client.clients.API.delete
   :noindex:

.. code-block:: python

    username = 'alice'
    edge.api.delete(f'/config/auth/users/{username}')  # Not recommended: Delete the user 'alice'

    edge.users.delete(username)  # Recommended


Supported Modules
-----------------


Data Types and Enumerators
--------------------------
Certain modules require input parameters comprising of complex data types or values selected from predefined lists. 
Complex data types are available in ``edge_types`` module, while ``edge_enum`` offers a comprehensive list of options for closed selection.
In the following example, we construct an access control entry (ACE) object using the ``edge_types`` and ``edge_enum`` modules.
This access control entry is then used to create a share.

.. code-block:: python

    from cterasdk import edge_types, edge_enum

    account_type = edge_enum.LG  # LG = Local Group
    file_access = edge_enum.FileAccessMode.RO  # RO = Read Only
    
    """Create an access control entry for the ACME domain administrators group"""
    domain_admins = edge_types.ShareAccessControlEntry(account_type, r'ACME\Domain Admins', file_access)

    """Create a CIFS/SMB network share allowing access to the ACME domain administrators group."""
    edge.shares.add('acme-project', 'cloud/users/Service Account/acme-project', acl=[domain_admins])

Complex types and predefined lists that are common to the CTERA Drive, Edge, and Portal are in ``common_types`` and ``common_enum``.


File Access
-----------
The SDK features a file browser module for managing files.

.. code-block:: python

    edge.files.mkdir('The/quick/brown/fox')  # Creates the dir 'fox' in the following path: 'The/quick/brown'
    edge.files.makedirs('The/quick/brown/fox')  # Creates the entire directory path recursively
    edge.files.copy('', destination=)
    edge.files.move('', destination=)
    edge.files.delete('The/quick/brown/fox/document.docx')
    edge.files.download('The/quick/brown/fox/document.docx')
    edge.files.download_as_zip('The/quick/brown/fox', ['document.docx', 'chart.xlsx', 'deck.pptx'])

Remote Access
-------------
If you are not within the same network as your CTERA Edge Filer, 
you can use remote access if the Edge Filer is connected to the Portal.

Once connected to CTERA Portal, every Edge Filer is assigned a fully qualified domain name. 
The FQDN is comprised of the Edge Filer's hostname and the address of the Portal it's connected to.

To connect to an Edge Filer remotely:
.. code-block:: python

    edge_hostname = 'edge-hostname'
    portal_address = 'tenant.ctera.com'
    with Edge(base=f'{edge_hostname}.{portal_address}') as edge:
        edge.login('edge-admin-username', 'edge-admin-password')
        # ...your code...

