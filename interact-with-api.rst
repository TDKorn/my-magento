..  Title: MyMagento
..  Description: A Python package that wraps and extends the Magento 2 REST API
..  Author: TDKorn

.. |Tip| replace:: 💡 **Tip**
.. |RTD| replace:: **Explore the docs »**
.. _RTD: https://my-magento.readthedocs.io/en/latest/
.. |api_endpoint| replace:: API endpoint
.. _api_endpoint: https://adobe-commerce.redoc.ly/2.3.7-admin/
.. |.Client| replace:: ``Client``
.. _.Client: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378
.. |.Model| replace:: ``Model``
.. _.Model: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241
.. |.SearchQuery| replace:: ``SearchQuery``
.. _.SearchQuery: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313
.. |.Order| replace:: ``Order``
.. _.Order: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/order.py#L12-L182
.. |.Product| replace:: ``Product``
.. _.Product: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/product.py#L12-L388
.. |.APIResponse| replace:: ``APIResponse``
.. _.APIResponse: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L244-L286
.. |.get_api| replace:: ``get_api()``
.. _.get_api: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/__init__.py#L16-L39
.. |.authenticate| replace:: ``authenticate()``
.. _.authenticate: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L227-L254
.. |.execute| replace:: ``execute()``
.. _.execute: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L130-L141
.. |.search| replace:: ``search()``
.. _.search: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L144-L167
.. |.by_id| replace:: ``by_id()``
.. _.by_id: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L143-L158
.. |.by_list| replace:: ``by_list()``
.. _.by_list: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L160-L188
.. |.get| replace:: ``get()``
.. _.get: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L199-L204
.. |.url_for| replace:: ``url_for()``
.. _.url_for: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L115-L142
.. |.post| replace:: ``post()``
.. _.post: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L206-L212
.. |.put| replace:: ``put()``
.. _.put: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L214-L220
.. |.delete| replace:: ``delete()``
.. _.delete: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L222-L227
.. |.add_criteria| replace:: ``add_criteria()``
.. _.add_criteria: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L44-L111
.. |.restrict_fields| replace:: ``restrict_fields()``
.. _.restrict_fields: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L113-L128
.. |.until| replace:: ``until()``
.. _.until: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L216-L227
.. |.since| replace:: ``since()``
.. _.since: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L190-L214
.. |.Model.refresh| replace:: ``Model.refresh()``
.. _.Model.refresh: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L131-L165
.. |.set_alt_text| replace:: ``set_alt_text()``
.. _.set_alt_text: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/models/product.py#L502-L512
.. |.ProductSearch.by_sku| replace:: ``by_sku()``
.. _.ProductSearch.by_sku: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L690-L695
.. |.ACCESS_TOKEN| replace:: ``ACCESS_TOKEN``
.. _.ACCESS_TOKEN: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/clients.py#L72
.. |.USER_CREDENTIALS| replace:: ``USER_CREDENTIALS``
.. _.USER_CREDENTIALS: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/clients.py#L67-L70
.. |.Client.scope| replace:: ``Client.scope``
.. _.Client.scope: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L22
.. |.scope| replace:: ``scope``
.. _.scope: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L22
.. |.result| replace:: ``result``
.. _.result: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L229-L241
.. |.views| replace:: ``views``
.. _.views: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L410-L413


Performing a |.search|_
~~~~~~~~~~~~~~~~~~~~~~~~~

The |.search|_ method lets you |.execute|_ a query on any |api_endpoint|_

It creates a |.SearchQuery|_ for the endpoint,
allowing you to retrieve data for

* An individual item (ex. |.by_id|_)
* A list of items (ex. |.by_list|_)
* Any search criteria you desire (see `Building Custom Search Queries <https://my-magento.readthedocs.io/en/latest/interact-with-api.html#custom-queries>`_)

|


.. raw:: html

   <table>
      <tr align="left">
         <th>📚 From the Docs... </th>
      </tr>
      <tr>
         <td>
            <dl class="py method">
                <dt class="sig sig-object py">
                <span class="sig-prename descclassname"><span class="pre">Client.</span></span><span class="sig-name descname"><span class="pre">search</span></span><span class="sig-paren">(</span><em class="sig-param"><span class="n"><span class="pre">endpoint</span></span></em><span class="sig-paren">)</span>
                <dd><p>


Initializes and returns a |.SearchQuery|_ corresponding to the specified ``endpoint``

.. raw:: html

   <table>
      <tr align="left">
         <th>📝 Note</th>
      </tr>
      <tr>
      <td>
         <p>


Several endpoints have predefined |.SearchQuery|_ and |.Model|_ subclasses

| If a subclass hasn’t been defined for the ``endpoint`` yet, a general |.SearchQuery|_ will be returned,
| which wraps the |.result|_ with |.APIResponse|_)


.. raw:: html

       </p>
     </td></tr>
   </table>
   <dl class="field-list simple">
      <dt class="field-odd">Parameters</dt>
         <dd class="field-odd"><p><strong>endpoint</strong> (<a class="reference external" href="https://docs.python.org/3/library/stdtypes.html#str" title="(in Python v3.11)"><em>str</em></a>) – a valid Magento API search endpoint</p></dd>
         <dt class="field-even">Return type</dt>
         <dd class="field-even"><p><em>

|.SearchQuery|_


.. raw:: html

          </em></p>
       </dd>
    </dl></dd></td></tr>
    </table>

|

Example: |.search|_ an endpoint |.by_id|_
===========================================

.. code-block:: python

    # Query the "invoices" endpoint (also: api.invoices)
    >>> api.search("invoices").by_id(1)

    <Magento Invoice: "#000000001"> for <Magento Order: "#000000001" placed on 2022-11-01 03:27:33>


|

Example: |.search|_ an endpoint |.by_list|_
==============================================

.. code-block:: python

    # Retrieve invoices from a list of invoice ids
    >>> ids = list(range(1,101))
    >>> api.invoices.by_list("entity_id", ids)

    [<Magento Invoice: "#000000001"> for <Magento Order: "#000000001" placed on 2022-11-01 03:27:33>, ...]

|

Search Results: The |.Model|_ Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. |the_models| replace:: the ``magento.models`` subpackage
.. _the_models: models.html

The |.result|_ of any |.SearchQuery|_ will be parsed and wrapped by a
|.Model|_ class in |the_models|_.

These classes make the API response data easier to work with.

They also provide endpoint-specific methods to update store data and search for related items.

|

Example: Retrieving every |.Order|_  containing a |.Product|_
==================================================================

Let's retrieve a |.Product|_ using |.ProductSearch.by_sku|_

.. code-block:: python

   >>> product = api.products.by_sku("24-MB01")

We can search for orders containing this product as follows:

.. code-block:: python

    # Using the Product itself
    >>> product.get_orders()

    [<Magento Order: "#000000003" placed on 2022-12-21 08:09:33>, ... ]

    # Using an OrderSearch
    >>> api.orders.by_product(product)
    >>> api.orders.by_product_id(product.id)
    >>> api.orders.by_sku(product.sku)

    [<Magento Order: "#000000003" placed on 2022-12-21 08:09:33>, ... ]

|

Example: Retrieving some items related to a `Category <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/category.py#L12-L146>`_
====================================================================================================================================================================================================================================

.. code-block:: python

    # Get Category data
    >>> category = api.categories.by_name("Watches")
    >>> category.get_products()
    >>> category.get_invoices()

    [<Magento Product: 24-MG04>, <Magento Product: 24-MG01>, <Magento Product: 24-MG03>, ... ]
    [<Magento Invoice: "#000000004"> for <Magento Order: "#000000004" placed on 2022-11-14 03:27:33>, ... ]

|

Example: Updating the Thumbnail `MediaEntry <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/product.py#L391-L556>`_ of a |.Product|_
======================================================================================================================================================

.. code-block:: python

    # Update product thumbnail label on specific store view
   >>> product.thumbnail.set_alt_text("bonjour", scope="FR")
   >>> print(product.thumbnail)

    <MediaEntry 3417 for <Magento Product: 24-MB01>: bonjour>

|

.. raw:: html

   <table>
      <tr align="left">
        <th>💡 Tip: Set the Store Scope</th>
      </tr>
      <tr>
         <td>


If you have multiple store views, a ``store_code`` can be specified when
retrieving/updating data

* The |.Client.scope|_ is used by default - simply change it to switch store |.views|_
* Passing the ``scope`` keyword argument to |.url_for|_, |.Model.refresh|_,
  and some Model update methods (like |.set_alt_text|_ above) will temporarily override the Client's scope


.. raw:: html

   </td></tr>
   </table>

|

.. _Custom Queries:

Building Custom Search Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the predefined methods, you can also build your own queries

* Simply |.add_criteria|_, |.restrict_fields|_, and |.execute|_ the search
* The |.since|_ and |.until|_ methods allow you to further filter your query by date

|

.. raw:: html

   <table>
      <tr align="left">
        <th>📄 Example: Retrieve Orders Over $50 Placed Since the Start of 2023</th>
      </tr>
      <tr>
         <td>


.. code-block:: python

    >>> api.orders.add_criteria(
    ...    field="grand_total",
    ...    value="50",
    ...    condition="gt"
    ... ).since("2023-01-01").execute()

    [<Magento Order: "#000000012" placed on 2023-01-02 05:19:55>, <Magento Order: "#000000013" placed on 2023-01-05 09:24:13>]

.. raw:: html

   </td></tr>
   </table>

|

Making Authorized Requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The |.Client|_ can be used to generate the |.url_for|_ any API endpoint,
including a store |.scope|_.

You can use this URL to make an authorized
|.get|_, |.post|_, |.put|_, or |.delete|_ request


Example: Making a |.get|_ Request
==================================

.. code-block:: python

 # Request the data for credit memo with id 7
 >>> url = api.url_for('creditmemo/7')
 >>> response = api.get(url)
 >>> print(response.json())

 {'adjustment': 1.5, 'adjustment_negative': 0, 'adjustment_positive': 1.5, 'base_adjustment': 1.5,  ... }


|


.. raw:: html

   <table>
      <tr align="left">
         <th>📝 Note</th>
      </tr>
      <tr>
         <td>

|  Using a |.search|_ is simpler than making |.get|_ requests, since the |.result|_ is wrapped by |.APIResponse|_ or other |.Model|_

.. code-block:: python

   # Retrieve credit memo with id 7 using a search
   >>> memo = api.search("creditmemo").by_id(7)
   >>> print(memo.data)
   >>> print(memo)

   {'adjustment': 1.5, 'adjustment_negative': 0, 'adjustment_positive': 1.5, 'base_adjustment': 1.5,  ... }
   <magento.models.model.APIResponse object at 0x000001BA42FD0FD1>

.. raw:: html

   </td></tr>
   </table>
