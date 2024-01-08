from __future__ import annotations
import re
from functools import cached_property
from typing import Union, Type, Iterable, List, Optional, Dict, TYPE_CHECKING
from .models import Model, APIResponse, Product, Category, ProductAttribute, Order, OrderItem, Invoice, Customer
from .exceptions import MagentoError
from . import clients

if TYPE_CHECKING:
    from typing_extensions import Self
    from . import Client


class SearchQuery:

    """Queries any endpoint that invokes the searchCriteria interface. Parent of all endpoint-specific search classes

    .. tip:: See https://developer.adobe.com/commerce/webapi/rest/use-rest/performing-searches/ for official docs
    """

    def __init__(self, endpoint: str, client: Client, model: Type[Model] = APIResponse):
        """Initialize a SearchQuery object

        :param endpoint: the base search API endpoint (for example, ``orders``)
        :param client: an initialized :class:`~.Client` object
        :param model: the :class:`~.Model` to parse the response data with; uses :class:`~.APIResponse` if not specified
        """
        if not isinstance(client, clients.Client):
            raise TypeError(f'`client` must be of type {clients.Client}')

        #: The :class:`~.Client` to send the search request with
        self.client = client
        #: The endpoint being queried
        self.endpoint = endpoint
        #: :doc:`models` class to wrap the response with
        self.Model = model
        #: The current url for the search request
        self.query = self.client.url_for(endpoint) + '/?'
        #: Restricted fields, from :meth:`~.restrict_fields`
        self.fields = ''
        #: The raw response data, if any
        self._result = {}

    def add_criteria(self, field, value, condition='eq', **kwargs) -> Self:
        """Add criteria to the search query

        :param field: the API response field to search by
        :param value: the value of the field to compare
        :param condition: the comparison condition
        :param kwargs: additional search option arguments (``group`` and ``filter``)
        :returns: the calling SearchQuery object

        .. admonition:: Keyword Argument Options: ``Condition``
           :class: tip

           The ``condition`` argument specifies the condition used to evaluate the attribute value

           * ``"eq"`` (default): matches items for which ``field=value``
           * ``"gt"``: matches items for which ``field>value``
           * ``"lt"``: matches items for which ``field<value``
           * ``"gteq"``: matches items for which ``field>=value``
           * ``"lteq"``: matches items for which ``field<=value``
           * ``"in"``: matches items for which ``field in value.split(",")``

             - Tip: for ``in``, use :meth:`~.by_list` if not building a complex query

           .. admonition:: Example
              :class: example

              ::

               # Search for Orders created in 2023
               >>> orders = api.orders.add_criteria(
               ...     field="created_at",
               ...     value="2023-01-01",
               ...     condition='gteq'
               ... ).execute()

        .. admonition:: Keyword Argument Options: Using Filter Groups
           :class: hint

           ``group`` - filter group number

           ``filter`` - filter number (within the specified filter group)


        *Using Filter Groups*

            Filter groups are filter criteria in the form of { field: value }

                Group 0 Filter 0                        ->      Filter 0
                Group 0 Filter 0 + Group 0 Filter 1     ->      Filter 0 OR Filter 1
                Group 0 Filter 0 + Group 1 Filter 0     ->      Filter 0 AND Filter 0
        """

        options = {
            'condition': condition,
            'group': self.last_group + 1,
            'filter': 0,
        }
        options.update(kwargs)

        criteria = (
                f'searchCriteria[filter_groups][{options["group"]}][filters][{options["filter"]}][field]={field}' +
                f'&searchCriteria[filter_groups][{options["group"]}][filters][{options["filter"]}][value]={value}' +
                f'&searchCriteria[filter_groups][{options["group"]}][filters][{options["filter"]}][condition_type]={options["condition"]}'
        )
        if not self.query.endswith('?'):
            self.query += '&'
        self.query += criteria
        return self

    def restrict_fields(self, fields: Iterable[str]) -> Self:
        """Constrain the API response data to only contain the specified fields

        :param fields: an iterable or comma separated string of fields to include in the response
        :returns: the calling SearchQuery object
        """
        if not isinstance(fields, str):
            if not isinstance(fields, Iterable):
                raise TypeError('"fields" must be a comma separated string or an iterable')
            fields = ','.join(fields)

        if (id_field := self.Model.IDENTIFIER) not in fields:
            fields += f',{id_field}'

        self.fields = f'&fields=items[{fields}]'
        return self

    def execute(self) -> Optional[Model | List[Model]]:
        """Sends the search request using the current :attr:`~.scope` of the :attr:`client`

        .. tip:: Change the :attr:`.Client.scope` to retrieve :attr:`~.result` data
           from different store :attr:`~.views`

        :returns: the search query :attr:`~.result`
        """
        response = self.client.get(self.query + self.fields)
        self.__dict__.pop('result', None)
        self._result = response.json()
        return self.result

    def by_id(self, item_id: Union[int, str]) -> Optional[Model]:
        """Retrieve data for an individual item by its id

        .. note:: The ``id`` field used is different depending on the endpoint being queried

           * Most endpoints use an ``entity_id`` or ``id``
           * The ``orders/items`` endpoint uses ``item_id``
           * The ``products`` endpoint uses ``product_id``,
             but can also be queried :meth:`~ProductSearch.by_sku`

           The :attr:`~.Model.IDENTIFIER` attribute of each :class:`~.Model` contains the appropriate field

        :param item_id: id of the item to retrieve
        """
        self.query = self.query.strip('?') + str(item_id)
        return self.execute()

    def by_list(self, field: str, values: Iterable) -> Optional[Model, List[Model]]:
        """Search for multiple items using an iterable or comma-separated string of field values

        .. admonition:: Examples
           :class: example

           Retrieve :class:`~.Product` with ids from 1 to 10::

            # Values can be a list/tuple/iterable
            >> api.products.by_list('entity_id', range(1,11))

           Search for :class:`~.Order` that are processing, pending, or completed::

            #  Values can be a comma-separated string
            >> api.orders.by_list('status', 'processing,pending,completed')


        :param field: the API response field to search for matches in
        :param values: an iterable or comma separated string of values
        """
        if not isinstance(values, Iterable):
            raise TypeError('`values` must be an iterable')
        if not isinstance(values, str):
            values = ','.join(f'{value}' for value in values)
        return self.add_criteria(
            field=field,
            value=values,
            condition='in'
        ).execute()

    def get_all(self) -> Optional[Model, List[Model]]:
        """Retrieve all items for the given search endpoint.

        .. warning:: Not guaranteed to work with all endpoints.
        """
        return self.since().execute()

    def since(self, sinceDate: str = None) -> Self:
        """Retrieve items for which ``created_at >= sinceDate``

        **Example**::

            # Retrieve products created in 2023
            >> api.products.since('2023-01-01').execute()


        .. tip:: Calling with no arguments retrieves all items

           ::

            # Retrieve all products
            >> api.products.since().execute()

        :param sinceDate: the date for response data to start from
        :return: the calling :class:`~SearchQuery`
        """
        return self.add_criteria(
            field='created_at',
            value=sinceDate,
            condition='gteq',
            group=self.last_group + 1,
        )

    def until(self, toDate: str) -> Self:
        """Retrieve items for which ``created_at <= toDate``

        :param toDate: the date for response data to end at (inclusive)
        :return: the calling :class:`~SearchQuery`
        """
        return self.add_criteria(
            field='created_at',
            value=toDate,
            condition='lteq',
            group=self.last_group + 1,
        )

    @cached_property
    def result(self) -> Optional[Model | List[Model]]:
        """The result of the search query, wrapped by the :class:`~.Model` corresponding to the endpoint

        :returns: the API response as either an individual or list of :class:`~.Model` objects
        """
        result = self.validate_result()
        if result is None:
            return result
        if isinstance(result, list):
            return [self.parse(item) for item in result]
        if isinstance(result, dict):
            return self.parse(result)

    def validate_result(self) -> Optional[Dict | List[Dict]]:
        """Parses the response and returns the actual result data, regardless of search approach"""
        if not self._result:
            return None

        if isinstance(self._result, list):
            return self._result

        if self._result.get('message'):  # Error; logged by Client
            return None

        if len(self._result.keys()) > 3:  # Single item, retrieved by id
            return self._result

        if 'items' in self._result:  # All successful responses with search criteria have `items` key
            items = self._result['items']
            if items:  # Response can still be {'items': None} though
                if len(items) > 1:
                    return items
                return items[0]
            else:
                self.client.logger.info(
                    "No matching {} for this search query".format(self.endpoint)
                )
                return None
        # I have no idea what could've gone wrong, sorry :/
        msg = "Search failed with an unknown error.\nAPI Response: {}".format(self._result)
        raise MagentoError(self.client, msg)

    def parse(self, data: dict) -> Model:
        """Parses the API response with the corresponding :class:`~.Model` object

        :param data: API response data of a single item
        """
        if self.Model is not APIResponse:
            return self.Model(data, self.client)
        return self.Model(data, self.client, self.endpoint)

    def reset(self) -> None:
        """Resets the query and result, allowing the object to be reused"""
        self._result = {}
        self.fields = ''
        self.query = self.client.url_for(self.endpoint) + '/?'
        self.__dict__.pop('result', None)

    @property
    def result_count(self) -> int:
        """Number of items that matched the search criteria"""
        if not self._result or not self.result:
            return 0
        if isinstance(self.result, Model):
            return 1
        return len(self.result)

    @property
    def result_type(self) -> Type:
        """The type of the result"""
        return type(self.result)

    @property
    def last_group(self) -> int:
        """The most recent filter group on the query
        
        :returns: the most recent filter group, or ``-1`` if no criteria has been added
        """
        if self.query.endswith('?'):
            return -1
        return int(re.match(
            r'.*searchCriteria\[filter_groups]\[(\d)]',
            self.query
        ).groups()[-1])


class OrderSearch(SearchQuery):

    """:class:`SearchQuery` subclass for the ``orders`` endpoint"""

    def __init__(self, client: Client):
        """Initialize an :class:`OrderSearch`

        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            endpoint='orders',
            client=client,
            model=Order
        )

    def by_number(self, order_number: Union[int, str]) -> Optional[Order]:
        """Retrieve an :class:`~.Order` by number

        :param order_number: the order number (``increment_id``)
        """
        return self.add_criteria(
            field='increment_id',
            value=order_number
        ).execute()

    def by_product(self, product: Product) -> Optional[Order | List[Order]]:
        """Search for all :class:`~.Order` s of a :class:`~.Product`

        :param product: the :class:`~.Product` to search for in orders
        """
        items = self.client.order_items.by_product(product)
        return self.from_items(items)

    def by_sku(self, sku: str) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` by product sku

        .. note:: Like :meth:`.OrderItemSearch.by_sku`, the sku will need to be an exact
           match to the sku of a simple product, including a custom option if applicable

           * Use :meth:`~.OrderSearch.by_product` or :meth:`~.OrderSearch.by_product_id`
             to find orders containing any of the :attr:`~.option_skus` and/or all
             :attr:`~.children` of a configurable product

        :param sku: the exact product sku to search for in orders
        """
        items = self.client.order_items.by_sku(sku)
        return self.from_items(items)

    def by_product_id(self, product_id: Union[int, str]) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` s by ``product_id``

        :param product_id: the ``id`` (``product_id``) of the product to search for in orders
        """
        items = self.client.order_items.by_product_id(product_id)
        return self.from_items(items)

    def by_category_id(self, category_id: Union[int, str], search_subcategories: bool = False) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` s by ``category_id``

        :param category_id: id of the category to search for in orders
        :param search_subcategories: if ``True``, also searches for orders from :attr:`~.all_subcategories`
        :returns: any :class:`~.Order` containing a :class:`~.Product` in the corresponding :class:`~.Category`
        """
        items = self.client.order_items.by_category_id(category_id, search_subcategories)
        return self.from_items(items)

    def by_category(self, category: Category, search_subcategories: bool = False) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` s that contain any of the category's :attr:`~.Category.products`

        :param category: the :class:`~.Category` to use in the search
        :param search_subcategories: if ``True``, also searches for orders from :attr:`~.all_subcategories`
        :returns: any :class:`~.Order` that contains a product in the provided category
        """
        items = self.client.order_items.by_category(category, search_subcategories)
        return self.from_items(items)

    def by_skulist(self, skulist: Union[str, Iterable[str]]) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` s using a list or comma separated string of product SKUs

        :param skulist: an iterable or comma separated string of product SKUs
        """
        items = self.client.order_items.by_skulist(skulist)
        return self.from_items(items)

    def by_customer(self, customer: Customer) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` s by :class:`~.Customer`

        :param customer: the :class:`~.Customer` to retrieve orders from
        """
        return self.by_customer_id(customer.uid)

    def by_customer_id(self, customer_id: Union[int, str]) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` s by ``customer_id``

        :param customer_id: the ``id`` of the customer to retrieve orders for
        """
        return self.add_criteria(
            field='customer_id',
            value=str(customer_id)
        ).execute()

    def from_items(self, items: Optional[OrderItem | List[OrderItem]]) -> Optional[Order, List[Order]]:
        """Retrieve unique :class:`~.Order` objects from :class:`~.OrderItem` entries using a single request

        :param items: an individual/list of order items
        """
        if items is None:
            return
        if isinstance(items, list):
            order_ids = set(item.order_id for item in items)
            return self.by_list('entity_id', order_ids)
        else:
            return items.order  # Single OrderItem


class OrderItemSearch(SearchQuery):

    """:class:`SearchQuery` subclass for the ``orders/items`` endpoint"""

    def __init__(self, client: Client):
        """Initialize an :class:`OrderItemSearch`

        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            endpoint='orders/items',
            client=client,
            model=OrderItem
        )

    @cached_property
    def result(self) -> Optional[OrderItem | List[OrderItem]]:
        if result := super().result:
            if isinstance(result, list):
                return [item for item in result if item]
        return result

    def parse(self, data) -> Optional[OrderItem]:
        """Overrides :meth:`SearchQuery.parse` to fully hydrate :class:`~.OrderItem` objects

        Extra validation is required for OrderItems, as duplicated and/or incomplete data is returned
        when the child of a configurable product is searched :meth:`by_sku` or :meth:`by_product`

        :param data: API response data
        """
        if data.get('parent_item'):
            return None
        if parent_id := data.get('parent_item_id'):
            return self.client.order_items.by_id(parent_id)
        else:
            return OrderItem(data, self.client)

    def by_product(self, product: Product) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries by :class:`~.Product`

        .. note:: This will match OrderItems that contain

           * Any of the child products of a configurable product
           * Any of the :attr:`~.option_skus` of a product with custom options

        :param product: the :class:`~.Product` to search for in order items
        """
        if not isinstance(product, Product):
            raise TypeError(f'`product` must be of type {Product}')

        if items := self.by_product_id(product.id):
            return items

        self.reset()
        return self.by_sku(product.encoded_sku)

    def by_sku(self, sku: str) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries by product sku.

        .. admonition:: The SKU must be an exact match to the OrderItem SKU

           OrderItems always use the SKU of a simple product, including any custom options.
           This means that:

           * Searching the SKU of a configurable product returns nothing
           * If a product has custom options, the search will only find OrderItems
             that contain the specific option sku (or base sku) that's provided

           To search for OrderItems containing all :attr:`~.children` of a
           configurable product and/or all possible :attr:`~.option_skus`,
           use :meth:`~.by_product` or :meth:`~.by_product_id`

        :param sku: the exact product sku to search for in order items
        """
        return self.add_criteria('sku', Model.encode(sku)).execute()

    def by_product_id(self, product_id: Union[int, str]) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries by product id.

        :param product_id: the ``id`` (``product_id``) of the :class:`~.Product` to search for in order items
        """
        return self.add_criteria('product_id', product_id).execute()

    def by_category_id(self, category_id: Union[int, str], search_subcategories: bool = False) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries by ``category_id``

        :param category_id: id of the :class:`~.Category` to search for in order items
        :param search_subcategories: if ``True``, also searches for order items from :attr:`~.all_subcategories`
        :returns: any :class:`~.OrderItem` containing a :class:`~.Product` in the corresponding :class:`~.Category`
        """
        if category := self.client.categories.by_id(category_id):
            return self.by_category(category, search_subcategories)

    def by_category(self, category: Category, search_subcategories: bool = False) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries that contain any of the category's :attr:`~.Category.products`

        :param category: the :class:`~.Category` to use in the search
        :param search_subcategories: if ``True``, also searches for order items from :attr:`~.all_subcategories`
        """
        if not isinstance(category, Category):
            raise TypeError(f'`category` must be of type {Category}')

        product_ids = category.all_product_ids if search_subcategories else category.product_ids
        return self.by_list('product_id', product_ids)

    def by_skulist(self, skulist: Union[str, Iterable[str]]) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem`s using a list or comma-separated string of product SKUs

        :param skulist: an iterable or comma separated string of product SKUs
        """
        if not isinstance(skulist, Iterable):
            raise TypeError(f'`skulist` must be an iterable or comma-separated string of SKUs')
        if isinstance(skulist, str):
            skulist = skulist.split(',')

        skus = map(Model.encode, skulist)
        return self.by_list('sku', skus)


class InvoiceSearch(SearchQuery):

    """:class:`SearchQuery` subclass for the ``invoices`` endpoint"""

    def __init__(self, client: Client):
        """Initialize an :class:`InvoiceSearch`

        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            endpoint='invoices',
            client=client,
            model=Invoice
        )

    def by_number(self, invoice_number: Union[int, str]) -> Optional[Invoice]:
        """Retrieve an :class:`~.Invoice` by number

        :param invoice_number: the invoice number (``increment_id``)
        """
        return self.add_criteria(
            field='increment_id',
            value=invoice_number
        ).execute()

    def by_order_number(self, order_number: Union[int, str]) -> Optional[Invoice]:
        """Retrieve an :class:`~.Invoice` by order number

        :param order_number: the order number (``increment_id``)
        """
        if order := self.client.orders.by_number(order_number):
            return self.by_order(order)

    def by_order(self, order: Order) -> Optional[Invoice]:
        """Retrieve the :class:`~.Invoice` for an :class:`~.Order`

        :param order: the :class:`~.Order` object to retrieve an invoice for
        """
        return self.by_order_id(order.id)

    def by_order_id(self, order_id: Union[int, str]) -> Optional[Invoice]:
        """Retrieve an :class:`~.Invoice` by ``order_id``

        :param order_id: the ``order_id`` of the order to retrieve an invoice for
        """
        return self.add_criteria(
            field='order_id',
            value=order_id
        ).execute()

    def by_product(self, product: Product) -> Optional[Invoice | List[Invoice]]:
        """Search for all :class:`~.Invoice` s of a :class:`~.Product`

        :param product: the :class:`~.Product` to search for in invoices
        """
        items = self.client.order_items.by_product(product)
        return self.from_order_items(items)

    def by_sku(self, sku: str) -> Optional[Invoice | List[Invoice]]:
        """Search for :class:`~.Invoice` s by product sku

        .. note:: Like :meth:`.OrderItemSearch.by_sku`, the sku will need to be an exact
           match to the sku of a simple product, including a custom option if applicable

           * Use :meth:`~.InvoiceSearch.by_product` or :meth:`~.InvoiceSearch.by_product_id`
             to find orders containing any of the :attr:`~.option_skus` and/or all
             :attr:`~.children` of a configurable product

        :param sku: the exact product sku to search for in invoices
        """
        items = self.client.order_items.by_sku(sku)
        return self.from_order_items(items)

    def by_product_id(self, product_id: Union[int, str]) -> Optional[Invoice | List[Invoice]]:
        """Search for :class:`~.Invoice` s by ``product_id``

        :param product_id: the ``id`` (``product_id``) of the product to search for in invoices
        """
        items = self.client.order_items.by_product_id(product_id)
        return self.from_order_items(items)

    def by_category_id(self, category_id: Union[int, str], search_subcategories: bool = False) -> Optional[Invoice | List[Invoice]]:
        """Search for :class:`~.Invoice` s by ``category_id``

        :param category_id: id of the category to search for in orders
        :param search_subcategories: if ``True``, also searches for orders from :attr:`~.all_subcategories`
        :returns: any :class:`~.Invoice` containing a :class:`~.Product` in the corresponding :class:`~.Category`
        """
        items = self.client.order_items.by_category_id(category_id, search_subcategories)
        return self.from_order_items(items)

    def by_category(self, category: Category, search_subcategories: bool = False) -> Optional[Invoice | List[Invoice]]:
        """Search for :class:`~.Invoice` s that contain any of the category's :attr:`~.Category.products`

        :param category: the :class:`~.Category` to use in the search
        :param search_subcategories: if ``True``, also searches for orders from :attr:`~.all_subcategories`
        :returns: any :class:`~.Invoice` that contains a product in the provided category
        """
        items = self.client.order_items.by_category(category, search_subcategories)
        return self.from_order_items(items)

    def by_skulist(self, skulist: Union[str, Iterable[str]]) -> Optional[Invoice | List[Invoice]]:
        """Search for :class:`~.Invoice` s using a list or comma separated string of product SKUs

        :param skulist: an iterable or comma separated string of product SKUs
        """
        items = self.client.order_items.by_skulist(skulist)
        return self.from_order_items(items)

    def by_customer(self, customer: Customer) -> Optional[Invoice | List[Invoice]]:
        """Search for all :class:`~.Invoice` s of a :class:`~.Customer`

        :param customer: the :class:`~.Customer` to search for in invoices
        :returns: any :class:`~.Invoice` associated with the provided :class:`~.Customer`
        """
        return self.by_customer_id(customer.uid)

    def by_customer_id(self, customer_id: Union[int, str]) -> Optional[Invoice | List[Invoice]]:
        """Search for :class:`~.Invoice` s by ``customer_id``

        :param customer_id: the ``id`` of the customer to retrieve invoices for
        """
        orders = self.client.orders.by_customer_id(customer_id)

        if isinstance(orders, list):
            order_ids = set(order.id for order in orders)
            return self.by_list('order_id', order_ids)
        else:
            return self.by_order_id(orders.id)

    def from_order_items(self, items: Optional[OrderItem | List[OrderItem]]) -> Optional[Invoice, List[Invoice]]:
        """Retrieve unique :class:`~.Invoice` objects from :class:`~.OrderItem` entries using a single request

        .. tip:: Since there is no ``invoices/items`` endpoint, to search for invoices we must first do an
           :class:`OrderItemSearch`, then retrieve the ``order_ids`` and search :meth:`~.by_order_id`

        :param items: an individual/list of order items
        """
        if items is None:
            return self.client.logger.info(
                'No matching invoices for this search query'
            )
        if isinstance(items, list):
            order_ids = set(item.order_id for item in items)
            return self.by_list('order_id', order_ids)
        else:
            return self.by_order_id(items.order_id)  # Single OrderItem


class ProductSearch(SearchQuery):

    """:class:`SearchQuery` subclass for the ``products`` endpoint"""

    def __init__(self, client: Client):
        """Initialize a :class:`ProductSearch`

        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            endpoint='products',
            client=client,
            model=Product
        )

    @property
    def attributes(self) -> ProductAttributeSearch:
        """Alternate way to access the SearchQuery for :class:`~.ProductAttribute` data"""
        return ProductAttributeSearch(self.client)

    def by_id(self, item_id: Union[int, str]) -> Optional[Product]:
        """Retrieve a :class:`~.Product` by ``product_id``

        .. note:: Response data from the ``products`` endpoint only has an ``id`` field, but
           all other endpoints that return data about products will use ``product_id``

        :param item_id: the ``id`` (``product_id``) of the product
        """
        return self.add_criteria(
            field='entity_id',  # Product has no "entity_id" field in API responses
            value=item_id  # But to search by the "id" field, must use "entity_id"
        ).execute()

    def by_sku(self, sku) -> Optional[Product]:
        """Retrieve a :class:`~.Product` by ``sku``

        :param sku: the product sku
        """
        return super().by_id(Model.encode(sku))

    def by_skulist(self, skulist: Union[str, Iterable[str]]) -> Optional[Product | List[Product]]:
        """Search for :class:`~.Product`s using a list or comma separated string of SKUs

        :param skulist: an iterable or comma separated string of SKUs
        """
        if not isinstance(skulist, Iterable):
            raise TypeError(f'`skulist` must be an iterable or comma-separated string of SKUs')
        if isinstance(skulist, str):
            skulist = skulist.split(',')

        skus = map(Model.encode, skulist)
        return self.by_list('sku', skus)

    def by_category(self, category: Category, search_subcategories: bool = False) -> Optional[Product | List[Product]]:
        """Search for :class:`~.Product` s in a :class:`~.Category`

        :param category: the :class:`~.Category` to retrieve products from
        :param search_subcategories: if ``True``, also retrieves products from :attr:`~.all_subcategories`
        """
        if not isinstance(category, Category):
            raise TypeError(f'`category` must be of type {Category}')

        if search_subcategories:
            category_ids = [category.id] + category.all_subcategory_ids
            return self.by_list('category_id', category_ids)
        else:
            return self.add_criteria('category_id', category.id).execute()

    def by_category_id(self, category_id: Union[int, str], search_subcategories: bool = False) -> Optional[Product | List[Product]]:
        """Search for :class:`~.Product` s by ``category_id``

        :param category_id: the id of the :class:`~.Category` to retrieve products from
        :param search_subcategories: if ``True``, also retrieves products from :attr:`~.all_subcategories`
        """
        if search_subcategories:
            if category := self.client.categories.by_id(category_id):
                return self.by_category(category, search_subcategories)
            return None
        else:
            return self.add_criteria('category_id', category_id).execute()

    def by_customer_id(self, customer_id: Union[int, str], exclude_cancelled: bool = True):
        """Search for ordered :class:`~.Product`\s by ``customer_id``

        :param customer_id: the ``id`` of the customer to retrieve ordered products for
        :param exclude_cancelled: flag indicating if products from cancelled orders should be excluded
        :returns: products that the customer has ordered, as an individual or list of :class:`~.Product` objects
        """
        if customer := self.client.customers.by_id(customer_id):
            return customer.get_ordered_products(exclude_cancelled)

    def get_stock(self, sku) -> Optional[int]:
        """Retrieve the :attr:`~.stock` of a product by sku

        :param sku: the product sku
        """
        if product := self.by_sku(sku):
            return product.stock


class ProductAttributeSearch(SearchQuery):

    """:class:`SearchQuery` subclass for the ``products/attributes`` endpoint"""

    def __init__(self, client: Client):
        """Initialize a :class:`ProductAttributeSearch`

        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            endpoint='products/attributes',
            client=client,
            model=ProductAttribute
        )

    def get_all(self) -> Optional[List[ProductAttribute]]:
        """Retrieve a list of all :class:`~.ProductAttribute`s"""
        return self.add_criteria('position', 0, 'gteq').execute()

    def by_code(self, attribute_code: str) -> Optional[ProductAttribute]:
        """Retrieve a :class:`~.ProductAttribute` by its attribute code

        :param attribute_code: the code of the :class:`~.ProductAttribute`
        """
        return self.by_id(attribute_code)

    def get_types(self) -> Optional[List[APIResponse]]:
        """Retrieve a list of all available :class:`~.ProductAttribute` types"""
        return self.client.search(f'{self.endpoint}/types').execute()


class CategorySearch(SearchQuery):

    """:class:`SearchQuery` subclass for the ``categories`` endpoint"""

    def __init__(self, client: Client):
        """Initialize a :class:`CategorySearch`

        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            endpoint='categories',
            client=client,
            model=Category
        )

    def by_id(self, item_id: Union[int, str]) -> Optional[Category]:
        self.query += f'rootCategoryId={item_id}'
        return self.execute()

    def by_list(self, field: str, values: Iterable) -> Optional[Category, List[Category]]:
        self.query = self.query.replace('categories', 'categories/list')
        return super().by_list(field, values)

    def get_root(self) -> Category:
        """Retrieve the top level/default :class:`~.Category` (every other category is a subcategory)"""
        return self.execute()

    def get_all(self) -> List[Category]:
        """Retrieve a list of all categories"""
        self.query = self.query.replace('categories', 'categories/list') + 'searchCriteria[currentPage]=1'
        return self.execute()

    def by_name(self, name: str, exact: bool = True) -> Optional[Category | List[Category]]:
        """Search for a :class:`~.Category` by name

        :param name: the category name to search for
        :param exact: whether the name should be an exact match
        """
        self.query = self.query.replace('categories', 'categories/list')
        if exact:
            return self.add_criteria('name', name).execute()
        else:
            return self.add_criteria('name', f'%25{name}%25', 'like').execute()


class CustomerSearch(SearchQuery):
    """:class:`SearchQuery` subclass for the ``customers/search`` endpoint"""

    def __init__(self, client: Client):
        """Initialize a :class:`CustomerSearch`

        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            endpoint='customers/search',
            client=client,
            model=Customer
        )

    def by_id(self, item_id: Union[int, str]) -> Optional[Customer]:
        self.query = self.query.replace('customers/search', 'customers')
        return super().by_id(item_id)

    def by_first_name(self, name):
        return self.add_criteria('firstName', name).execute()

    def by_last_name(self, name):
        return self.add_criteria('lastName', name).execute()

    def by_invoice(self, invoice: Invoice):
        return self.by_order(invoice.order)

    def by_order(self, order: Order):
        if customer_id := order.data.get("customer_id"):
            return self.by_id(customer_id)
        else:
            return self.client.logger.info(
                f"No customer account exists for {order}")

    def by_product(self, product: Product) -> Optional[Customer | List[Customer]]:
        orders = product.get_orders() or []
        customer_ids = set()

        if not isinstance(orders, list):
            return self.by_order(orders)

        for order in orders:
            if customer_id := order.data.get('customer_id'):
                customer_ids.add(customer_id)

        return self.by_list('entity_id', customer_ids)
