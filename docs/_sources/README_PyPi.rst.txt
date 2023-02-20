..  Title: MyMagento
..  Description: A Python package that wraps and extends the Magento 2 REST API
..  Author: TDKorn

.. |Tip| replace:: 💡 **Tip**
.. |RTD| replace:: **Explore the docs »**
.. _RTD: https://my-magento.readthedocs.io/en/latest/
.. |api_endpoint| replace:: API endpoint
.. _api_endpoint: https://adobe-commerce.redoc.ly/2.3.7-admin/
.. |.Client| replace:: Client
.. _.Client: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378
.. |.Model| replace:: Model
.. _.Model: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241
.. |.SearchQuery| replace:: SearchQuery
.. _.SearchQuery: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313
.. |.execute| replace:: execute()
.. _.execute: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L130-L141
.. |.ACCESS_TOKEN| replace:: ACCESS_TOKEN
.. _.ACCESS_TOKEN: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/clients.py#L72
.. |.USER_CREDENTIALS| replace:: USER_CREDENTIALS
.. _.USER_CREDENTIALS: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/clients.py#L67-L70


MyMagento🛒
---------------

.. image:: https://i.imgur.com/dkCWWYn.png
   :alt: Magento Logo
   :align: center
   :width: 200
   :height: 175

A Python package that wraps and extends the Magento 2 REST API

|RTD|_

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

|

About MyMagento
~~~~~~~~~~~~~~~~~~~~

.. |note| replace:: 📝

+-------------------------------------------------------------+
| |note| What's MyMagento?                                    |
+=============================================================+
|  ``MyMagento`` is a highly interconnected package that      |
|  wraps and extends the Magento 2 REST API, providing a more |
|  intuitive and user-friendly interface to access and update |
|  your store                                                 |
+-------------------------------------------------------------+


MyMagento simplifies interaction with the Magento 2 REST API
=================================================================

If you've worked with the Magento 2 API, you'll know that not all endpoints are created equally.

``MyMagento`` aims to streamline your workflow by simplifying a
variety of commonly needed API operations.


Main Components
==================================

.. .. image:: https://user-images.githubusercontent.com/96394652/212470049-ebc2c46b-1fb1-44d1-a400-bf3cdfd3e4fb.png
   :alt: The Client
   :target: https://github.com/TDKorn/my-magento/blob/sphinx-docs/magento/clients.py

.. |comp| replace:: 💻
.. |mag| replace:: 🔍

+-------------------------------------------------------------+
| |comp| The |.Client|_                                       |
+=============================================================+
|  * Handles all API interactions                             |
|  * Supports multiple store views                            |
|  * Provides access to all other package components          |
+-------------------------------------------------------------+

+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+
| |mag| The |.SearchQuery|_ and Subclasses                                                                                                                        |
+=================================================================================================================================================================+
|  * |.execute|_ a predefined or custom search query on any endpoint                                                                                              |
|  * Simplified creation of basic and advanced `searches using REST endpoints <https://developer.adobe.com/commerce/webapi/rest/use-rest/performing-searches/>`_  |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------+
| 🧠 The |.Model|_ Subclasses                                                |
+============================================================================+
| * Wrap all API responses in the package                                    |
| * Provide additional endpoint-specific methods to retrieve and update data |
+----------------------------------------------------------------------------+


Available Endpoints
======================

``MyMagento`` is compatible with every |api_endpoint|_

Endpoints are wrapped with a :class:`~.Model` and :class:`~.SearchQuery` subclass as follows:

+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| **Endpoint**             | **Client Shortcut**                 |:class:`~.SearchQuery` **Subclass**|:class:`~.Model` **Subclass**|
+==========================+=====================================+===================================+=============================+
| ``orders``               | ``Client.orders``                   | :class:`~.OrderSearch`            | :class:`~.Order`            |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``orders/items``         | ``Client.order_items``              | :class:`~.OrderItemSearch`        | :class:`~.OrderItem`        |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``invoices``             | ``Client.invoices``                 | :class:`~.InvoiceSearch`          | :class:`~.Invoice`          |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``products``             | ``Client.products``                 | :class:`~.ProductSearch`          | :class:`~.Product`          |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``products/attributes``  | ``Client.product_attributes``       | :class:`~.ProductAttributeSearch` | :class:`~.ProductAttribute` |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``categories``           | ``Client.categories``               | :class:`~.CategorySearch`         | :class:`~.Category`         |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+
| ``endpoint``             | ``Client.search("endpoint")``       | :class:`~.SearchQuery`            | :class:`~.APIResponse`      |
+--------------------------+-------------------------------------+-----------------------------------+-----------------------------+

...

⚙ Installing MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~

To install using ``pip``::

   pip install my-magento

Please note that ``MyMagento`` requires ``Python >= 3.10``


📚 Documentation
~~~~~~~~~~~~~~~~~

Full documentation can be found on `ReadTheDocs <https://my-magento.readthedocs.io/en/latest/>`_


...

QuickStart: Login with MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``MyMagento`` uses the :class:`~.Client` class to handle all interactions with the API

.. _login: https://my-magento.readthedocs.io/en/latest/examples/logging-in.html
.. |login| replace:: Get a Magento 2 REST API Token With ``MyMagento``


+-------------------------------------------------------------+
| |Tip|                                                       |
+=============================================================+
| See |login|_ for full details on generating an access token |
+-------------------------------------------------------------+


Setting the Login Credentials
===================================

To generate an |.ACCESS_TOKEN|_ you'll need to :meth:`~.authenticate` your |.USER_CREDENTIALS|_

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
=========================================================================================================

Option 1: Initialize a :class:`~.Client` Directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

      from magento import Client

      >>> api = Client(domain, username, password, **kwargs)


Option 2: Call :func:`~.get_api`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python


      import magento

      >>> api = magento.get_api(**kwargs)

:func:`.get_api` takes the same keyword arguments as the :class:`~.Client`, but if the ``domain``, ``username``, or ``password``
are missing, it will attempt to use the following environment variables:


.. code-block:: python

   import os

   os.environ['MAGENTO_DOMAIN'] = domain
   os.environ['MAGENTO_USERNAME']= username
   os.environ['MAGENTO_PASSWORD']= password

...

Getting an |.ACCESS_TOKEN|_
=======================================

Unless you specify ``login=False``, the :class:`~.Client` will automatically call :meth:`~.authenticate` once initialized


.. code-block:: python

   >>> api.authenticate()

   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
   |[ MyMagento | website_username ]|:  Logged in to username

