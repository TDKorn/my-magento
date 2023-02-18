..  Title: MyMagento
..  Description: A Python package that wraps and extends the Magento 2 REST API
..  Author: TDKorn

.. |Tip| replace:: 💡 **Tip**
.. |RTD| replace:: **Explore the docs »**
.. _RTD: https://my-magento.readthedocs.io/en/latest/
.. |api_endpoints| replace:: API endpoints
.. _api_endpoints: https://adobe-commerce.redoc.ly/2.3.7-admin/
.. |.Client| replace:: ``Client``
.. _.Client: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378
.. |.Model| replace:: ``Model``
.. _.Model: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241
.. |.SearchQuery| replace:: ``SearchQuery``
.. _.SearchQuery: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313
.. |.get_api| replace:: ``get_api()``
.. _.get_api: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/__init__.py#L16-L39
.. |.authenticate| replace:: ``authenticate()``
.. _.authenticate: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L227-L254
.. |.execute| replace:: ``execute()``
.. _.execute: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L130-L141
.. |.ACCESS_TOKEN| replace:: ``ACCESS_TOKEN``
.. _.ACCESS_TOKEN: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/clients.py#L72
.. |.USER_CREDENTIALS| replace:: ``USER_CREDENTIALS``
.. _.USER_CREDENTIALS: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/clients.py#L67-L70


.. raw:: html

   <div align="center">

.. image:: https://my-magento.readthedocs.io/en/latest/_static/magento_orange.png
   :alt: MyMagento: Magento 2 REST API wrapper
   :width: 15%

.. raw:: html

   <h1>MyMagento🛒</h1>


A Python package that wraps and extends the Magento 2 REST API


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

.. raw:: html

   <table>
      <tr align="left">
         <th>📝 What's MyMagento?</th>
      </tr>
      <tr>
         <td>


``MyMagento`` is a highly interconnected package that wraps and extends the Magento 2 REST API,
providing a more intuitive and user-friendly interface to access and update your store.

.. raw:: html

   </td></tr>
   </table>


MyMagento simplifies interaction with the Magento 2 REST API
=================================================================

If you've worked with the Magento 2 API, you'll know that not all endpoints are created equally.

``MyMagento`` aims to streamline your workflow by simplifying a
variety of commonly needed API operations.

...

Main Components
==================================

.. .. image:: https://user-images.githubusercontent.com/96394652/212470049-ebc2c46b-1fb1-44d1-a400-bf3cdfd3e4fb.png
   :alt: The Client
   :target: https://github.com/TDKorn/my-magento/blob/sphinx-docs/magento/clients.py

.. raw:: html

   <table>
      <tr align="left">
         <th>

💻 The |.Client|_

.. raw:: html

   </th></tr>
   <tr><td>

* Handles all API interactions
* Supports multiple store views
* Provides access to all other package components‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎

.. raw:: html

   </td></tr>
   </table>

.. raw:: html

   <table>
      <tr align="left">
         <th>

🔍 The |.SearchQuery|_ and Subclasses

.. raw:: html

   </th></tr>
   <tr><td>

* |.execute|_  a predefined or custom search query on any endpoint
* Simplified creation of basic and advanced `searches using REST endpoints <https://developer.adobe.com/commerce/webapi/rest/use-rest/performing-searches/>`_ ‎

.. raw:: html

   </td></tr>
   </table>


.. raw:: html

   <table>
      <tr align="left">
         <th>

🧠 The |.Model|_ Subclasses

.. raw:: html

   </th></tr>
   <tr><td>

* Wrap all API responses in the package
* Provide additional endpoint-specific methods to retrieve and update data

.. raw:: html

   </td></tr>
   </table>


...

Available Endpoints
======================

``MyMagento`` is compatible with all |api_endpoints|_

Endpoints are wrapped with a |.Model|_ and |.SearchQuery|_ subclass as follows:

+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| **Endpoint**             | |.Client|_ **Shortcut**             | |.SearchQuery|_ **Subclass**                                                                             | |.Model|_ **Subclass**                                                                                     |
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
| ``endpoint``             | ``Client.search("endpoint")``       | `SearchQuery <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313>`_             | `APIResponse <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L244-L286>`_        |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+

...

⚙ Installing MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~

To install using ``pip``::

   pip install my-magento

Please note that ``MyMagento`` requires ``Python >= 3.10``


📚 Documentation
~~~~~~~~~~~~~~~~~~

Full documentation can be found on `ReadTheDocs <https://my-magento.readthedocs.io/en/latest/>`_


...

QuickStart: Login with MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``MyMagento`` uses the |.Client|_ class to handle all interactions with the API.

.. raw:: html

   <table>
      <tr align="left">
         <th>💡 Tip</th>
      </tr>
      <tr>
         <td>See
            <a href="https://my-magento.readthedocs.io/en/latest/examples/logging-in.html">Get a Magento 2 REST API Token With MyMagento</a>
            for full details on generating an access token</td>
      </tr>
   </table>

...

Setting the Login Credentials
===================================

To generate an |.ACCESS_TOKEN|_ you'll need to |.authenticate|_ your |.USER_CREDENTIALS|_

Creating a |.Client|_ requires a ``domain``, ``username``, and ``password`` at minimum.


.. code-block:: python

   >>> domain = 'website.com'
   >>> username ='username'
   >>> password = 'password'


If you're using a local installation of Magento you'll need to set ``local=True``. Your domain should look like this:

.. code-block:: python

   >>> domain = '127.0.0.1/path/to/magento'


...

Getting a |.Client|_
=================================

Option 1: Initialize a |.Client|_ Directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

      from magento import Client

      >>> api = Client(domain, username, password, **kwargs)


Option 2: Call |.get_api|_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python


      import magento

      >>> api = magento.get_api(**kwargs)

|.get_api|_ takes the same keyword arguments as the |.Client|_, but if the ``domain``, ``username``, or ``password``
are missing, it will attempt to use the following environment variables:


.. code-block:: python

   import os

   os.environ['MAGENTO_DOMAIN'] = domain
   os.environ['MAGENTO_USERNAME']= username
   os.environ['MAGENTO_PASSWORD']= password

...

Getting an |.ACCESS_TOKEN|_
=======================================

Unless you specify ``login=False``, the |.Client|_ will automatically call |.authenticate|_ once initialized


.. code-block:: python

   >>> api.authenticate()

   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
   |[ MyMagento | website_username ]|:  Logged in to username

