.. _available_endpoints:

Available Endpoints
~~~~~~~~~~~~~~~~~~~~~~~

The following endpoints are currently wrapped with a :class:`~.Model` and :class:`~.SearchQuery` subclass

.. csv-table::
   :header: "**Endpoint**", "**Client Shortcut**", ":class:`~.SearchQuery` **Subclass**", ":class:`~.Model` **Subclass**"

   "``orders``", ":attr:`.Client.orders`", ":class:`~.OrderSearch`", ":class:`~.Order`"
   "``orders/items``", ":attr:`.Client.order_items`", ":class:`~.OrderItemSearch`", ":class:`~.OrderItem`"
   "``invoices``", ":attr:`.Client.invoices`", ":class:`~.InvoiceSearch`", ":class:`~.Invoice`"
   "``products``", ":attr:`.Client.products`", ":class:`~.ProductSearch`", ":class:`~.Product`"
   "``products/attributes``", ":attr:`.Client.product_attributes`", ":class:`~.ProductAttributeSearch`", ":class:`~.ProductAttribute`"
   "``categories``", ":attr:`.Client.categories`", ":class:`~.CategorySearch`", ":class:`~.Category`"
   "``endpoint``", "``Client.search('endpoint')``", ":class:`~.SearchQuery`", ":class:`~.APIResponse`"
