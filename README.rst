****************
CTERA for Python
****************
.. image:: https://travis-ci.com/CTERA-Networks/ctera-python-sdk.svg?branch=master
   :target: https://travis-ci.com/CTERA-Networks/ctera-python-sdk
.. image:: https://readthedocs.org/projects/ctera-python-sdk/badge/?version=latest
   :target: https://ctera-python-sdk.readthedocs.io/en/latest/?badge=latest

A Python SDK for integrating with the CTERA Networks API. Compatible with Python
3.5+. Documentation is available on `Read the Docs <http://ctera-python-sdk.readthedocs.org/>`_.

Installation
------------
Installing via `pip <https://pip.pypa.io/>`_:

.. code-block:: console

    $ pip install cterasdk

Install from source:

.. code-block:: console

   $ git clone https://github.com/CTERA-Networks/ctera-python-sdk.git
   $ cd ctera-python-sdk
   $ python setup.py install

Importing the Library
---------------------
After installation, to get started, open a Python console:

.. code-block:: pycon

    >>> from cterasdk import *

Documentation
-------------
Documentation can be compiled by running ``make html`` from the ``docs``
folder. After compilation, open ``docs/build/html/index.html``. Alternatively,
you can read a hosted version from `Read the Docs`_.

Testing
-------
We use the `tox <https://tox.readthedocs.org/>`_ package to run tests in Python
3. To install, use :code:`pip install tox`. Once installed, run `tox` from the
root directory.

.. code-block:: console

   $ tox
