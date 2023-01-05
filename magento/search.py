from __future__ import annotations
from functools import cached_property
from typing import Union, Type, Iterable, List, Optional, Dict, TYPE_CHECKING
from .models import Model, APIResponse, Product, Category, ProductAttribute, Order, OrderItem, Invoice
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
            raise TypeError(f'client type must be {clients.Client}')

        self.client = client    #: the :class:`~.Client` to send the search request with
        self.endpoint = endpoint
        self.Model = model
        self.query = self.client.url_for(endpoint) + '/?'
        self.fields = ''
        self._result = {}

    def add_criteria(self, field, value, condition='eq', **kwargs) -> Self:
        """Add criteria to the search query

        :param field: the API response field to search by
        :param value: the value of the field to compare
        :param condition: the comparison condition
        :param kwargs: additional search option arguments (``group`` and ``filter``)
        :returns: the calling SearchQuery object

        *Options*
                condition:  condition used to evaluate the attribute value

                            (Default Value)     'eq'            =           (field=value)
                                                'gt'            >
                                                'lt'            <
                                                'gteq'          >=
                                                'lteq'          <=
                                                'in'            []


                group:      filter group number

                filter:     filter number (within the specified filter group)


        *Using Filter Groups*

            Filter groups are filter criteria in the form of { field: value }

                Group 0 Filter 0                        ->      Filter 0
                Group 0 Filter 0 + Group 0 Filter 1     ->      Filter 0 OR Filter 1
                Group 0 Filter 0 + Group 1 Filter 0     ->      Filter 0 AND Filter 0
        """

        options = {
            'condition': condition,
            'group': 0,
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

        # TODO:
        #  if self.Model.identifier not in fields:
        #  fields += f',{self.Model.identifier}'

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

        .. note:: The ``id`` used is different depending on the endpoint being queried

           * Most endpoints use an ``entity_id``
           * The ``orders/items`` endpoint uses ``item_id`` (see :class:`OrderItemSearch`)
           * The ``products`` endpoint can be queried either with the ``product_id``
             or :meth:`~.ProductSearch.by_sku`

        :param item_id: id of the item to retrieve
        """
        self.query = self.query.strip('?') + str(item_id)
        return self.execute()

    def by_list(self, field: str, values: Iterable) -> Optional[Model, List[Model]]:
        """Search for multiple items using an iterable or comma-separated string of field values

        .. admonition:: Example

           Search for orders that are processing, pending, or completed::

              #  Values can be a list/tuple/iterable
              >> api.orders.by_list('status', ['processing', 'pending', 'completed'])

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


class OrderSearch(SearchQuery):

    def __init__(self, client: Client):
        """SearchQuery for the ``orders`` endpoint

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
        :returns: any :class:`~.Order` containing a product linked to the provided category id
        """
        items = self.client.order_items.by_category_id(category_id)
        return self.from_items(items)

    def by_category(self, category: Category, search_subcategories: bool = False) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` s that contain any of the category's :attr:`~.Category.products`

        :param category: the :class:`~.Category` to use in the search
        :param search_subcategories: if ``True``, also searches for orders from :attr:`~.all_subcategories`
        :returns: any :class:`~.Order` that contains a product in the provided category
        """
        items = self.client.order_items.by_category(category)
        return self.from_items(items)

    def by_skulist(self, skulist: Union[str, Iterable[str]]) -> Optional[Order | List[Order]]:
        """Search for :class:`~.Order` s using a list or comma separated string of product SKUs

        .. note:: SKUs must be URL-encoded

        :param skulist: an iterable or comma separated string of product SKUs
        """
        items = self.client.order_items.by_skulist(skulist)
        return self.from_items(items)

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

    def __init__(self, client: Client):
        """SearchQuery for the ``orders/items`` endpoint

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

        return self.by_product_id(product.id)

    def by_sku(self, sku: str) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries by product sku.

        .. admonition:: The SKU must be an exact match to the OrderItem SKU

           OrderItems always use the SKU of a simple product, including any custom options.
           This means that:

           * Searching the SKU of a configurable product returns nothing
           * If a product has custom options, the search will only find OrderItems
             that contain the specific option sku (or base sku) that's provided

           To search for OrderItems containing all :attr:`~.children` and all possible
           :attr:`~.option_skus` of a product, use :meth:`~.by_product`

        :param sku: the exact product sku to search for in order items
        """
        return self.add_criteria('sku', Model.encode(sku)).execute()

    def by_product_id(self, product_id: Union[int, str]) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries by product id.

        :param product_id: the ``id`` (or ``product_id``) of the product to search for in order items
        """
        return self.add_criteria('product_id', product_id).execute()

    def by_category_id(self, category_id: Union[int, str]) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries by category id

        :param category_id: id of the category to search for in order items
        :returns: any :class:`~.OrderItem` containing a product linked to the provided category id
        """
        if category := self.client.categories.by_id(category_id):
            return self.by_category(category)

    def by_category(self, category: Category) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries that contain any of the category's :attr:`~.Category.products`

        :param category: the :class:`~.Category` to use in the search
        :returns: any :class:`~.OrderItem` that contains a product in the provided category
        """
        if not isinstance(category, Category):
            raise TypeError(f'`category` must be of type {Category}')

        product_ids = ','.join(f'{product.id}' for product in category.products)
        return self.by_list('product_id', product_ids)

    def by_skulist(self, skulist: Union[str, Iterable[str]]) -> Optional[OrderItem | List[OrderItem]]:
        """Search for :class:`~.OrderItem`s using a list or comma separated string of product SKUs

        .. note:: SKUs must be URL-encoded

        :param skulist: an iterable or comma separated string of product SKUs
        """
        return self.by_list('sku', skulist)


class InvoiceSearch(SearchQuery):

    def __init__(self, client: Client):
        """SearchQuery for the ``invoices`` endpoint

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
        """Retrieve an :class:`~.Invoice` by order id ``id``

        :param order_id: the ``order_id`` of the order to retrieve an invoice for
        """
        return self.add_criteria(
            field='order_id',
            value=order_id
        ).execute()


class ProductSearch(SearchQuery):

    def __init__(self, client: Client):
        """SearchQuery for the ``products`` endpoint

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

        :param item_id: the ``id`` (or ``product_id``) of the product
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

        .. note:: SKUs must be URL-encoded

        :param skulist: an iterable or comma separated string of SKUs
        """
        return self.by_list('sku', skulist)

    def by_category(self, category: str) -> list[Product]:
        """Search for :class:`~.Product`s by category name"""
        return self.client.categories.by_name(category).products

    def by_category_id(self, category_id: int):
        """Search for :class:`~.Product`s by category id"""
        return self.client.categories.by_id(category_id).products

    def get_stock(self, sku) -> Optional[int]:
        """Retrieve the :attr:`~.stock` of a product by sku

        :param sku: the product sku
        """
        if product := self.by_sku(sku):
            return product.stock


class ProductAttributeSearch(SearchQuery):

    def __init__(self, client: Client):
        """SearchQuery for the ``products/attributes`` endpoint

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

    def __init__(self, client: Client):
        """SearchQuery for the ``categories`` endpoint

        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            endpoint='categories',
            client=client,
            model=Category
        )

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
