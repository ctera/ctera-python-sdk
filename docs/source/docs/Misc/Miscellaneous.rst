*************
Miscellaneous
*************

Formatting
==========

The following formatting functions are included in this library:

.. py:function:: tojsonstr(obj[, pretty_print = True])

   Convert a Python object to a JSON string.
   
   :param obj: the Python object
   :param pretty_print: whether to format the JSON string, defaults to ``True``
   :type obj: obj
   :type pretty_print: bool
   
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

.. py:function:: toxmlstr(obj[, pretty_print = False])

   Convert a Python object to an XML string
   
   :param obj: the Python object
   :param pretty_print: whether to format the XML string, defaults to ``False``
   :type obj: obj
   :type pretty_print: bool

.. code-block:: python

   user = Object()
   user.name = 'alice'
   user.firstName = 'Alice'
   user.lastName = 'Wonderland'
   user.email = 'alice@adventures.com'
   user.password = 'Passw0rd1!'
   print(toxmlstr(user))
   print(toxmlstr(user, True))