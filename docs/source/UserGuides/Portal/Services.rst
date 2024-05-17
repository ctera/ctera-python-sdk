===============
Services Portal
===============

Logging In
==========

.. automethod:: cterasdk.objects.synchronous.core.ServicesPortal.login
   :noindex:

.. code-block:: python

   user.login('walice', 'G3neralZ0d!')

.. automethod:: cterasdk.objects.synchronous.core.ServicesPortal.logout
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


Miscellaneous
=============

.. automethod:: cterasdk.objects.synchronous.core.GlobalAdmin.test
   :noindex:

.. code-block:: python

   admin.test()

.. automethod:: cterasdk.objects.synchronous.core.GlobalAdmin.whoami
   :noindex:

.. code-block:: python

   admin.whoami()
