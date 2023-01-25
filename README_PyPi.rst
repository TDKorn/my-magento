..  Title: MyMagento
..  Description: A Python package that wraps and extends the Magento 2 REST API
..  Author: TDKorn

.. |Tip| replace:: 💡 **Tip**
.. |.Client| replace:: ``Client``
.. |.get_api| replace:: ``get_api()``
.. _.Client: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378
.. _.get_api: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/__init__.py#L16-L39

MyMagento🛒
---------------

.. image:: https://my-magento.readthedocs.io/en/latest/_static/magento_orange.png
   :alt: Magento Logo
   :align: center
   :width: 200
   :height: 175

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

|

About MyMagento
~~~~~~~~~~~~~~~~~~~~

.. admonition:: What's MyMagento?
   :class: note

   ``MyMagento`` is a highly interconnected package that wraps and extends the Magento 2 REST API,
   providing a more intuitive and user-friendly interface to access and update your store.


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

.. admonition:: The |.Client|_
   :class: client

   * Handles all API interactions
   * Supports multiple store views
   * Provides access to all other package components

.. admonition:: The `SearchQuery <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313>`_ and Subclasses
   :class: search

   * `execute() <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L130-L141>`_  a predefined or custom search query on any endpoint
   * Simplified creation of basic and advanced `searches using REST endpoints <https://developer.adobe.com/commerce/webapi/rest/use-rest/performing-searches/>`_


.. admonition::  The `Model <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241>`_ Subclasses
   :class: hint

   * Wrap all API responses in the package
   * Provide additional endpoint-specific methods to retrieve and update data


Available Endpoints
======================

The following endpoints are currently wrapped with a `Model <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241>`_ and `SearchQuery <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313>`_ subclass

+--------------------------+-------------------------------------+-----------------------------------+----------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| **Endpoint**             | **Client Attribute**                |`SearchQuery <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313>`_ **Subclass** |`Model <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241>`_ **Subclass**   |
+==========================+=====================================+==========================================================================================================+============================================================================================================+
| ``orders``               | ``Client.orders``                   | `OrderSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L316-L411>`_            | `Order <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/order.py#L12-L182>`_               |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``orders/items``         | ``Client.order_items``              | `OrderItemSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L414-L526>`_        | `OrderItem <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/order.py#L185-L292>`_          |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``invoices``             | ``Client.invoices``                 | `InvoiceSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L529-L654>`_          | `Invoice <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/invoice.py#L11-L57>`_            |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``products``             | ``Client.products``                 | `ProductSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L657-L744>`_          | `Product <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/product.py#L12-L388>`_           |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``products/attributes``  | ``Client.product_attributes``       | `ProductAttributeSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L747-L775>`_ | `ProductAttribute <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/product.py#L559-L588>`_ |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``categories``           | ``Client.categories``               | `CategorySearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L778-L820>`_         | `Category <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/category.py#L12-L146>`_         |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+

...

Installation
~~~~~~~~~~~~~~~~~~~

.. admonition:: Installing MyMagento
   :class: client

   To install using ``pip``::

    pip install my-magento

   Please note that ``MyMagento`` requires ``Python >= 3.10``


Documentation
~~~~~~~~~~~~~~

Full documentation can be found on `ReadTheDocs <https://www.my-magento.readthedocs.io/en/latest/>`_


...

QuickStart: Login with MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



+-----------------------------------------------------------------------------------------------------------------------------------------+
| |Tip|                                                                                                                                   |
+=========================================================================================================================================+
| See `logging-in <https://my-magento.readthedocs.io/en/latest/examples/logging-in.html>`_ for full details on generating an access token |
+----------------------------------------------------------------------+------------------------------------------------------------------+



Setting the Login Credentials
===================================
The credentials of your Magento 2 admin account are used to initialize and `authenticate() <https://github.com/tdkorn/my-magento/blob/9db95d3ac755a1a2475006197a46fe49be881168/magento/clients.py#L227-L254>`_ a |.Client|_

.. code-block:: python

   >> domain = 'website.com'
   >> username ='username'
   >> password = 'password'


If you're using a local installation of Magento, your domain should look like this:

.. code-block:: python

   >> domain = '127.0.0.1/path/to/magento'


Getting a |.Client|_
=================================

MyMagento uses the |.Client|_
in one of two ways

Method 1: Initialize a |.Client|_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from magento import Client

   >>> api = Client(domain, username, password)

   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
   |[ MyMagento | website_username ]|:  Logged in to username


Method 2: Initialize a |.Client|_ with |.get_api|_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The |.get_api|_ method uses the same keyword arguments as the |.Client|_, but will try
using environment variable values if the domain, username, or password are missing



.. code-block:: python


      import magento

      >>> api = magento.get_api()

      |[ MyMagento | website_username ]|:  Authenticating username on website.com...
      |[ MyMagento | website_username ]|:  Logged in to username



Now let's start `interacting with the api <https://my-magento.readthedocs.io/en/latest/interact-with-api.html#interact-with-api>`_
