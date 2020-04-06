****************
CTERA for Python
****************
.. image:: https://travis-ci.com/ctera/ctera-python-sdk.svg?branch=master
   :target: https://travis-ci.com/ctera/ctera-python-sdk
.. image:: https://readthedocs.org/projects/ctera-python-sdk/badge/?version=latest
   :target: https://ctera-python-sdk.readthedocs.io/en/latest/?badge=latest
.. image:: https://snyk.io/test/github/ctera/ctera-python-sdk/badge.svg?targetFile=ut-requirements.txt
   :target: https://snyk.io/test/github/ctera/ctera-python-sdk?targetFile=ut-requirements.txt

A Python SDK for integrating with the CTERA Global File System API. Compatible with Python
3.5+. 

Documentation
-------------
User documentation is available on `Read the Docs <http://ctera-python-sdk.readthedocs.org/>`_.

Installation
------------
Installing via `pip <https://pip.pypa.io/>`_:

.. code-block:: console

    $ pip install cterasdk

Install from source:

.. code-block:: console

   $ git clone https://github.com/ctera/ctera-python-sdk.git
   $ cd ctera-python-sdk
   $ python setup.py install

Importing the Library
---------------------
After installation, to get started, open a Python console:

.. code-block:: pycon

    >>> from cterasdk import *

Building Documentation
-------------------------
Documentation can be compiled by running ``make html`` from the ``docs``
folder. After compilation, open ``docs/build/html/index.html``. 

Testing
-------
We use the `tox <https://tox.readthedocs.org/>`_ package to run tests in Python
3. To install, use :code:`pip install tox`. Once installed, run `tox` from the
root directory.

.. code-block:: console

   $ tox
