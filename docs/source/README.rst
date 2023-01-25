..  Title: MyMagento
..  Description: A Python package that wraps and extends the Magento 2 REST API
..  Author: TDKorn

.. raw:: html

   <div align="center">

.. image:: _static/magento_orange.png
   :alt: MyMagento: Magento 2 REST API wrapper
   :width: 15%

.. raw:: html

   <h1>MyMagento🛒</h1>


A Python package that wraps and extends the Magento 2 REST API

.. |RTD| replace:: **Explore the docs »**
.. _RTD: https://my-magento.readthedocs.io/en/latest/

|RTD|_


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
   <br/>
   <br/>

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


Main Components
==================================

.. .. image:: https://user-images.githubusercontent.com/96394652/212470049-ebc2c46b-1fb1-44d1-a400-bf3cdfd3e4fb.png
   :alt: The Client
   :target: https://github.com/TDKorn/my-magento/blob/sphinx-docs/magento/clients.py

.. admonition:: The :class:`~.Client`
   :class: client

   * Handles all API interactions
   * Supports multiple store views
   * Provides access to all other package components

.. admonition:: The :class:`~.SearchQuery` and Subclasses
   :class: search

   * :meth:`~.execute`  a predefined or custom search query on any endpoint
   * Simplified creation of basic and advanced `searches using REST endpoints <https://developer.adobe.com/commerce/webapi/rest/use-rest/performing-searches/>`_


.. admonition::  The :class:`~.Model` Subclasses
   :class: hint

   * Wrap all API responses in the package
   * Provide additional endpoint-specific methods to retrieve and update data


Available Endpoints
======================

The following endpoints are currently wrapped with a :class:`~.Model` and :class:`~.SearchQuery` subclass

+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| **Endpoint**             | **Client Attribute**                |:class:`~.SearchQuery` **Subclass**|:class:`~.Model` **Subclass**|
+==========================++====================================++==================================++============================+
| ``orders``               | :attr:`.Client.orders`              | :class:`~.OrderSearch`            | :class:`~.Order`            |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``orders/items``         | :attr:`.Client.order_items`         | :class:`~.OrderItemSearch`        | :class:`~.OrderItem`        |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``invoices``             | :attr:`.Client.invoices`            | :class:`~.InvoiceSearch`          | :class:`~.Invoice`          |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``products``             | :attr:`.Client.products`            | :class:`~.ProductSearch`          | :class:`~.Product`          |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``products/attributes``  | :attr:`.Client.product_attributes`  | :class:`~.ProductAttributeSearch` | :class:`~.ProductAttribute` |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``categories``           | :attr:`.Client.categories`          | :class:`~.CategorySearch`         | :class:`~.Category`         |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+

...

Installation
~~~~~~~~~~~~~~~~~~~

.. admonition:: Installing MyMagento
   :class: client

   To install using ``pip``::

    pip install my-magento

   Please note that ``MyMagento`` requires ``Python >= 3.10``


.. Documentation
.. ~~~~~~~~~~~~~~

.. Full documentation can be found on `ReadTheDocs <https://my-magento.readthedocs.io/en/latest/>`_


...

QuickStart: Login with MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. only:: draft


   +----------------------------------------------------------------------+
   | |Tip|                                                                |
   +======================================================================+
   | See :ref:`logging-in` for full details on generating an access token |
   +----------------------------------------------------------------------+


.. tip:: See :ref:`logging-in` for full details on generating an access token


Setting the Login Credentials
===================================

Use your Magento 2 login credentials to generate an :attr:`~.ACCESS_TOKEN`

.. code-block:: python

   >> domain = 'website.com'
   >> username ='username'
   >> password = 'password'


If you're using a local installation of Magento, your domain should look like this:

.. code-block:: python

   >> domain = '127.0.0.1/path/to/magento'


Getting a :class:`~.Client`
=================================

``MyMagento`` uses the :class:`~.Client` class to handle all interactions with the API

You'll need to create a :class:`~.Client` to :meth:`~.authenticate` your :attr:`~.USER_CREDENTIALS`



Option 1: Initialize a :class:`~.Client`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At minimum, you'll need a ``domain``, ``username``, and ``password``

* ``domain`` **Format**

   - **Hosted**: ``domain.com``
   - **Local**: ``127.0.0.1/path/to/magento`` (must also set ``local=True``)


.. code-block:: python

      from magento import Client

      >>> api = Client(domain, username, password)



Option 2: Call :func:`~.get_api`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :func:`.get_api()` method uses the same keyword arguments as the ``Client``, but will try
using environment variable values if the ``domain``, ``username``, or ``password`` are missing

.. code-block:: python


      import magento

      >>> api = magento.get_api()


Setting Environment Variables
````````````````````````````````````

To log in faster with :func:`~.get_api`, set the following environment variables:

.. code-block:: python

   import os

   os.environ['MAGENTO_DOMAIN'] = domain
   os.environ['MAGENTO_USERNAME']= username
   os.environ['MAGENTO_PASSWORD']= password


Output Either Way
====================

.. code-block:: python

      |[ MyMagento | website_username ]|:  Authenticating username on website.com...
      |[ MyMagento | website_username ]|:  Logged in to username



Once you've initialized a ``Client`` it's time to start `interacting with the api <https://my-magento.readthedocs.io/en/latest/interact-with-api.html#interact-with-api>`_
