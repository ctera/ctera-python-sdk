***************
End User Portal
***************

.. contents:: Table of Contents

Instantiate a Services Portal object
------------------------------------

.. py:class:: ServicesPortal(host[, port = 443][, https = True])

   :param host: The fully qualified domain name, hostname or an IPv4 address of the Gateway
   :param port: Set a custom port number (0 - 65535), defaults to ``443``
   :param https: Set to ``False`` to use HTTP, defaults to ``True``
   :type host: str
   :type port: int
   :type https: bool
   
.. code-block:: python

   user = ServicesPortal('chopin.ctera.com') # will use HTTPS over port 443
   
.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.http['ssl'] = 'Trust'``

Logging in
==========

.. py:method:: ServicesPortal.test()

   Verification check to ensure the target host is a Portal.
   
.. code-block:: python

   user.test()
   
.. py:method:: ServicesPortal.login(username, password)

   Login to CTERA Portal as an End User or a Team Portal admin.
   
.. code-block:: python

   user.login('admin', 'G3neralZ0d!')

.. py:method:: ServicesPortal.logout()

   Logout from CTERA Portal.
   
.. code-block:: python

   user.logout()