***************
End User Portal
***************

.. contents:: Table of Contents

Instantiate a Services Portal object
------------------------------------
.. autoclass:: cterasdk.object.Portal.ServicesPortal
   :special-members: __init__
   :noindex:

.. code-block:: python

   user = ServicesPortal('portal.ctera.com') # will use HTTPS over port 443

.. warning:: for any certificate related error, this library will prompt for your consent in order to proceed. to avoid the prompt, you may configure `chopin-core` to automatically trust the server's certificate, using: ``config.http['ssl'] = 'Trust'``

Logging in
==========
.. automethod:: cterasdk.object.Portal.ServicesPortal.test
   :noindex:

.. code-block:: python

   user.test()

.. automethod:: cterasdk.object.Portal.ServicesPortal.login
   :noindex:

.. code-block:: python

   user.login('walice', 'G3neralZ0d!')

.. automethod:: cterasdk.object.Portal.ServicesPortal.logout
   :noindex:

.. code-block:: python

   user.logout()
