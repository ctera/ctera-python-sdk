******************************
Tenant User and Administration
******************************

.. contents:: Table of Contents

Create a Services Portal Session
--------------------------------
.. autoclass:: cterasdk.objects.core.ServicesPortal
   :special-members: __init__
   :noindex:

.. code-block:: python

   user = ServicesPortal('portal.ctera.com') # will use HTTPS over port 443

.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.http['ssl'] = 'Trust'``


Logging in
==========
.. automethod:: cterasdk.objects.core.ServicesPortal.test
   :noindex:

.. code-block:: python

   user.test()

.. automethod:: cterasdk.objects.core.ServicesPortal.login
   :noindex:

.. code-block:: python

   user.login('walice', 'G3neralZ0d!')

.. automethod:: cterasdk.objects.core.ServicesPortal.logout
   :noindex:

.. code-block:: python

   user.logout()


Managing S3 Credentials
=======================
.. automethod:: cterasdk.core.credentials.S3.all
   :noindex:

.. code-block:: python

   """List all S3 credentials"""
   for credential in user.credentials.s3.all():
       print(credential.accessKey, credential.activated)

.. automethod:: cterasdk.core.credentials.S3.create
   :noindex:

.. code-block:: python

   """Create an S3 credential"""
   credential = user.credentials.s3.create()

.. automethod:: cterasdk.core.credentials.S3.delete
   :noindex:

.. code-block:: python

   """Delete an S3 credentials"""
   access_key_id = 'ABCDEFGHIJKLMOP'
   user.credentials.s3.delete(access_key_id)
