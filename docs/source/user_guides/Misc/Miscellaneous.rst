*************
Miscellaneous
*************

Formatting
==========

The following formatting functions are included in this library:

.. autofunction:: cterasdk.convert.format.tojsonstr
   :noindex:

.. code-block:: python

   user = Object()
   user.name = 'alice'
   user.firstName = 'Alice'
   user.lastName = 'Wonderland'
   user.email = 'alice@adventures.com'
   user.password = 'Passw0rd1!'
   print(tojsonstr(user))
   {
        "lastName": "Wonderland",
        "password": "Passw0rd1!",
        "name": "alice",
        "firstName": "Alice",
        "email": "alice@adventures.com"
   }
   print(tojsonstr(user, False))
   {"lastName": "Wonderland", "password": "Passw0rd1!", "name": "alice", "firstName": "Alice", "email": "alice@adventures.com"}

.. autofunction:: cterasdk.convert.format.toxmlstr
   :noindex:

.. code-block:: python

   user = Object()
   user.name = 'alice'
   user.firstName = 'Alice'
   user.lastName = 'Wonderland'
   user.email = 'alice@adventures.com'
   user.password = 'Passw0rd1!'
   print(toxmlstr(user))
   print(toxmlstr(user, True))
