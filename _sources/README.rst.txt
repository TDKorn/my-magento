..  Title: MyMagento
..  Description: A Python package that wraps and extends the Magento 2 REST API
..  Author: TDKorn

.. meta::
   :title: MyMagento
   :description: A Python package that wraps and extends the Magento 2 REST API

.. |RTD| replace:: **Explore the docs »**
.. _RTD: https://my-magento.readthedocs.io/en/latest/
.. |api_endpoint| replace:: API endpoint
.. _api_endpoint: https://adobe-commerce.redoc.ly/2.3.7-admin/


.. only:: pypi

   MyMagento🛒
   ---------------

   .. image:: https://i.imgur.com/dkCWWYn.png
      :alt: Logo for MyMagento: Python Magento 2 REST API Wrapper
      :align: center
      :width: 200
      :height: 175

.. raw:: html

   <div align="center">

.. only:: html or readme

   .. image:: _static/magento_orange.png
      :alt: Logo for MyMagento: Python Magento 2 REST API Wrapper
      :width: 15%

.. only:: html

   .. raw:: html

      <span class="h1">MyMagento🛒</span>

.. only:: readme

   .. raw:: html

      <h1>MyMagento🛒</h1>


A Python package that wraps and extends the Magento 2 REST API


|RTD|_

.. only:: pypi

   |

.. image:: https://img.shields.io/pypi/v/my-magento?color=eb5202
   :target: https://pypi.org/project/my-magento/
   :alt: PyPI Version

.. image:: https://img.shields.io/badge/GitHub-my--magento-4f1abc
   :target: https://github.com/tdkorn/my-magento
   :alt: GitHub Repository

.. image:: https://static.pepy.tech/personalized-badge/my-magento?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads
    :target: https://pepy.tech/project/my-magento

.. image:: https://readthedocs.org/projects/my-magento/badge/?version=latest
    :target: https://my-magento.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. raw:: html

   </div>

|

About MyMagento
~~~~~~~~~~~~~~~~~~~~

.. admonition:: What's MyMagento?
   :class: note

   ``MyMagento`` is a highly interconnected package that wraps and extends the Magento 2 REST API,
   providing a more intuitive and user-friendly interface to access and update your store.


.. rubric:: MyMagento simplifies interaction with the Magento 2 REST API

If you've worked with the Magento 2 API, you'll know that not all endpoints are created equally.

``MyMagento`` aims to streamline your workflow by simplifying a
variety of commonly needed API operations.

.. only:: readme

   ...

Main Components
==================================

.. admonition:: The :class:`~.Client`
   :class: client

   * Handles all API interactions
   * Supports multiple store views
   * Provides access to all other package components

.. admonition:: The :class:`~.SearchQuery` and Subclasses
   :class: search

   * :meth:`~.execute` a search query on any endpoint
   * Intuitive interface for :ref:`Custom Queries`
   * All predefined methods retrieve data using only 1-2 API requests

.. admonition::  The :class:`~.Model` Subclasses
   :class: hint

   * Wrap all API responses in the package
   * Provide additional endpoint-specific methods to retrieve and update data

.. only:: readme

   ...

Available Endpoints
======================

``MyMagento`` is compatible with every |api_endpoint|_

Endpoints are wrapped with a :class:`~.Model` and :class:`~.SearchQuery` subclass as follows:

.. include:: _snippets/available_endpoints.rst
   :start-line: 6


...

⚙ Installing MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~


To install using ``pip``::

   pip install my-magento

Please note that ``MyMagento`` requires ``Python >= 3.10``

...

.. only:: readme or pypi

   📚 Documentation
   ~~~~~~~~~~~~~~~~~~

   Full documentation can be found on `ReadTheDocs <https://my-magento.readthedocs.io/en/latest/>`_

   |

QuickStart: Login with MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``MyMagento`` uses the :class:`~.Client` class to handle all interactions with the API.

.. tip:: See :ref:`logging-in` for full details on generating an access token


Setting the Login Credentials
===================================

To generate an :attr:`~.ACCESS_TOKEN` you'll need to :meth:`~.authenticate` your :attr:`~.USER_CREDENTIALS`.

Creating a :class:`~.Client` requires a ``domain``, ``username``, and ``password`` at minimum.


.. code-block:: python

   >>> domain = 'website.com'
   >>> username ='username'
   >>> password = 'password'


If you're using a local installation of Magento you'll need to set ``local=True``. Your domain should look like this:

.. code-block:: python

   >>> domain = '127.0.0.1/path/to/magento'


...

Getting a :class:`~.Client`
=================================

Option 1: Initialize a :class:`~.Client` Directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

      from magento import Client

      >>> api = Client(domain, username, password, **kwargs)


Option 2: Call :func:`~.get_api`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python


      import magento

      >>> api = magento.get_api(**kwargs)

:func:`.get_api` takes the same keyword arguments as the :class:`~.Client`

* If the ``domain``, ``username``, or ``password`` are missing,
  it will attempt to use the following environment variables:


.. code-block:: python

   import os

   os.environ['MAGENTO_DOMAIN'] = domain
   os.environ['MAGENTO_USERNAME']= username
   os.environ['MAGENTO_PASSWORD']= password

...

Getting an :attr:`~.ACCESS_TOKEN`
=======================================

Unless you specify ``login=False``, the :class:`~.Client` will automatically call :meth:`~.authenticate` once initialized:


.. code-block:: python

   >> api.authenticate()

   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
   |[ MyMagento | website_username ]|:  Logged in to username


.. only:: readme or pypi

   |

   .. include:: interact-with-api.rst
      :start-line: 11
