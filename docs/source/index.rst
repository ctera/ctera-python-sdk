===============================
Welcome to the CTERA Python SDK
===============================

The CTERA SDK for Python provides developers with powerful tools to automate the deployment and configuration 
of the CTERA Global File System, streamline data management tasks, 
and seamlessly integrate CTERA's global namespace with their applications.

Current version is |release|.

.. _GitHub: https://github.com/ctera/ctera-python-sdk


Key Features
============

- Supports configuration management for CTERA Drive, Edge Filer and Portal, including remote access
- Supports managing CTERA Migrate
- Supports file access for CTERA Edge Filer and Portal


.. _cterasdk-installation:

Library Installation
====================

.. code-block:: bash

    $ pip install cterasdk


Getting Started
===============
Edge
----

.. code-block:: python

    import cterasdk.settings
    from cterasdk import Edge

    def main():
        cterasdk.settings.sessions.management.ssl = False  # for unstrusted or self-signed certificates
        with Edge('192.168.0.1') as edge:
            edge.login('admin-username', 'admin-password')
            print('Hostname: ', edge.config.get_hostname())
            print('Location: ', edge.config.get_location())

            edge.config.set_location('1234 Sycamore Lane, Humorville, NY 12345')
            print('Location: ', edge.config.get_location())

    if __name__ == '__main__':
        main()

This prints:

.. code-block:: text

    Hostname:  vGateway-01ad
    Location:  None
    Location:  1234 Sycamore Lane, Humorville, NY 12345

..


Portal
------

.. code-block:: python

    import cterasdk.settings
    from cterasdk import GlobalAdmin

    def main():
        cterasdk.settings.sessions.management.ssl = False  # for unstrusted or self-signed certificates
        with GlobalAdmin('tenant.ctera.com') as admin:
            admin.login('admin-username', 'admin-password')
            for user in admin.users.list_local_users(include=['firstName', 'lastName', 'email']):
                print(user)

            admin.portals.browse_global_admin()
            for administrator in admin.admins.list_admins(include['email']):
                print(administrator)

    if __name__ == '__main__':
        main()

This prints:

.. code-block:: text

    {
        "_classname": "PortalUser",
        "email": "alice.wonderland@acme.com",
        "firstName": "Alice",
        "lastName": "Wonderland",
        "name": "alice"
    }
    {
        "_classname": "PortalAdmin",
        "email": "matt@ctera.com",
        "name": "matt"
    }
    {
        "_classname": "PortalAdmin",
        "email": "saimon@ctera.com",
        "name": "saimon"
    }

..

Source Code
===========

The project is hosted on `GitHub <https://github.com/ctera/ctera-python-sdk>`_.


Documentation
=============
User documentation is available on `Read the Docs <http://ctera-python-sdk.readthedocs.org/>`_.


Bug Reporting
=============

Feel free to submit feature requests or issues via https://github.com/ctera/ctera-python-sdk/issues


Authors and License
===================

The ``cterasdk`` package is written mostly by Saimon Michelson and Ron Erez.

It's Apache 2 licensed and freely available.

Feel free to improve this package and send pull requests to `GitHub <https://github.com/ctera/ctera-python-sdk>`_.


Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: Navigation

   UserGuides/Edge/Index
   UserGuides/Portal/Index
   UserGuides/Miscellaneous/Index
   