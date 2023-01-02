from __future__ import annotations
from functools import cached_property
from typing import Union, Type, Iterable, List, Optional
from .models import Model, APIResponse, Product, Category, ProductAttribute, Order, OrderItem, Invoice
from . import clients


class SearchQuery:

    def __init__(self, endpoint: str, client: clients.Client, model: Type[Model] = APIResponse):
        if not isinstance(client, clients.Client):
            raise TypeError(f'client type must be {clients.Client}')

        self.client = client
        self.endpoint = endpoint
        self.Model = model
        self.query = self.client.url_for(endpoint) + '/?'
        self.fields = ''
        self._result = {}

    def add_criteria(self, field, value, condition='eq', **kwargs) -> SearchQuery:
        """
        :param field:       the object attribute to search by
        :param value:       the value of the attribute to compare
        :param condition:   the comparison condition
        :param kwargs:      additional search option arguments
        :return:            the calling SearchQuery object

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

    # Query -> &fields=items['field1,field2']
    def restrict_fields(self, fields: Union[str, list, tuple]) -> SearchQuery:
        if not isinstance(fields, str):
            if not isinstance(fields, (list, tuple)):
                raise TypeError('Invalid type for argument "fields". Must be a comma separated string or list/tuple.')
            fields = ','.join(fields)

        if 'entity_id' not in fields:
            fields = ','.join([fields, 'entity_id'])

        self.fields = f'&fields=items[{fields}]'
        return self

    def execute(self):
        """Sends the search request through the active client."""
        response = self.client.get(self.query + self.fields)
        self.__dict__.pop('result', None)
        self._result = response.json()
        return self.result

    def by_id(self, item_id: Union[int, str]) -> {}:
        self.query = self.query.strip('?') + str(item_id)
        return self.execute()

    def by_number(self, increment_id: str):
        return self.add_criteria(
            field='increment_id',
            value=increment_id
        ).execute()

    @cached_property
    def result(self) -> Union[Model, list[Model]]:
        result = self.validate_result()
        if result is None:
            return result
        if isinstance(result, list):
            return [self.parse(item) for item in result]
        if isinstance(result, dict):
            return self.parse(result)

    def validate_result(self) -> Union[dict, list[dict]]:
        """
        Returns the actual result, regardless of search approach
        Failed: response will always contain a "message" key
        Success:
            Search Query:   response contains up to 3 keys from ["items", "total_count", "search_criteria"]
            Direct Query:   response is the full entity/model response dict; typically has 20+ keys
        """
        if not self._result:
            return None

        if self._result.get('message'):
            print(
                'Search failed with the following message: ' + '\t'
                + self._result['message']
            )
            return None

        if len(self._result.keys()) > 3:    # Direct request of entity by id/sku with full response dict
            return self._result

        if 'items' in self._result:         # All successful response with search criteria will have items key
            items = self._result['items']   # Note that some entities (ex. Order) have an items key too. Entity response won't reach this line though
            if items:                       # Response can still be {'items': None} though
                if len(items) > 1:
                    return items
                return items[0]
            else:
                print("No matching {} for this search query".format(self.endpoint))
                return None
        else:  # I have no idea what could've gone wrong, sorry :/
            raise RuntimeError("Unknown Error. Raw Response: {}".format(self._result))

    def parse(self, data) -> Model:
        """Parses the API response and returns the corresponding entity/model object"""
        if self.Model is not APIResponse:
            return self.Model(data, self.client)
        return self.Model(data, self.client, self.endpoint)

    def reset(self) -> None:
        self._result = {}
        self.fields = ''
        self.query = self.client.url_for(self.endpoint) + '/?'
        self.__dict__.pop('result', None)

    @property
    def result_count(self) -> int:
        if not self._result or not self.result:
            return 0
        if isinstance(self.result, Model):
            return 1
        return len(self.result)

    @property
    def result_type(self):
        return type(self.result)


class OrderSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='orders',
            client=client,
            model=Order
        )


class OrderItemSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='orders/items',
            client=client,
            model=OrderItem
        )

    @cached_property
    def result(self) -> Union[Model, list[Model]]:
        if result := super().result:
            if isinstance(result, list):
                return [item for item in result if item]
        return result

    def parse(self, data) -> Optional[Model]:
        """Parses the API response data into fully hydrated :class:`~.OrderItem` objects

        Extra validation is required for OrderItems, as duplicated and/or incomplete data is returned when
        the child of a configurable product is searched :meth:`by_sku` or :meth:`by_product`

        :param data: API response data
        """
        if data.get('parent_item'):
            return None
        if parent_id := data.get('parent_item_id'):
            return self.client.order_items.by_id(parent_id)
        else:
            return super().parse(data)

    def by_product(self, product: Product) -> Union[OrderItem, List[OrderItem]]:
        """Search for :class:`OrderItem` entries by :class:`~.Product`

        .. note:: This will match OrderItems that contain

           * Any of the child products of a configurable product
           * Any of the :attr:`~.option_skus` of a product with custom options

        :param product: the :class:`~.Product` to search for in order items
        """
        return self.by_product_id(product.id)

    def by_sku(self, sku: str) -> Union[OrderItem, List[OrderItem]]:
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

    def by_product_id(self, product_id: Union[int, str]) -> Union[OrderItem, List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries by product id.

        :param product_id: the product id to search for in order items
        """
        return self.add_criteria('product_id', product_id).execute()

    def by_category_id(self, category_id: Union[int, str]) -> Union[OrderItem, List[OrderItem]]:
        """Search for :class:`OrderItem` entries by category id

        :param category_id: id of the category to search for in order items
        :returns: any :class:`~.OrderItem` containing a product linked to the provided category id
        """
        return self.by_category(self.client.categories.by_id(category_id))

    def by_category(self, category: Category) -> Union[OrderItem, List[OrderItem]]:
        """Search for :class:`~.OrderItem` entries that contain any of the category's :attr:`~.Category.products`

        :param category: the :class:`~.Category` to use in the search
        :returns: any :class:`~.OrderItem` that contains a product in the provided category
        """
        product_ids = ','.join(f'{product.id}' for product in category.products)
        return self.add_criteria(
            field='product_id',
            value=product_ids,
            condition='in'
        ).execute()

    def by_skulist(self, skulist: Union[str, Iterable[str]]) -> Union[OrderItem, List[OrderItem]]:
        """Search for :class:`~.OrderItem`s using a list or comma separated string of product SKUs

        .. note:: SKUs must be URL-encoded

        :param skulist: an iterable or comma separated string of product SKUs
        """
        if not isinstance(skulist, Iterable):
            raise TypeError
        if not isinstance(skulist, str):
            skulist = ','.join(skulist)
        return self.add_criteria(
            field='sku',
            value=skulist,
            condition='in'
        ).execute()


class InvoiceSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='invoices',
            client=client,
            model=Invoice
        )

    def by_order_number(self, order_number):
        if order := self.client.orders.by_number(order_number):
            return self.by_order(order)

    def by_order(self, order):
        return self.by_order_id(order.id)

    def by_order_id(self, order_id):
        return self.add_criteria(
            field='order_id',
            value=order_id
        ).execute()


class ProductSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='products',
            client=client,
            model=Product
        )

    @property
    def attributes(self):
        return ProductAttributeSearch(self.client)

    def by_id(self, item_id: Union[int, str]) -> {}:
        return self.add_criteria(
            field='entity_id',  # Product has no "entity_id" field in API responses, just "id"
            value=item_id       # But to search by the "id" field, need to use "entity_id"
        ).execute()

    def by_sku(self, sku) -> Product:
        return super().by_id(self.Model.encode(sku))

    def by_skulist(self, skulist: Union[str, Iterable[str]]) -> list[Product]:
        """Search for :class:`~.Product`s using a list or comma separated string of SKUs

        .. note:: SKUs must be URL-encoded

        :param skulist: an iterable or comma separated string of SKUs
        """
        if not isinstance(skulist, Iterable):
            raise TypeError
        if not isinstance(skulist, str):
            skulist = ','.join(skulist)
        return self.add_criteria(
            field='sku',
            value=skulist,
            condition='in'
        ).execute()

    def by_category(self, category: str) -> list[Product]:
        """Search for :class:`~.Product`s by category name"""
        return self.client.categories.by_name(category).products

    def by_category_id(self, category_id: int):
        """Search for :class:`~.Product`s by category id"""
        return self.client.categories.by_id(category_id).products

    def get_stock(self, sku):
        return self.by_sku(sku).stock

    def get_enabled_simple_skus(self):
        self.add_criteria(
            field='type_id',
            value='simple'
        ).add_criteria(
            field='status',
            value=Product.STATUS_ENABLED,
            group=1
        )
        return self.execute()


class ProductAttributeSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='products/attributes',
            client=client,
            model=ProductAttribute
        )

    def get_all(self):
        return self.add_criteria('position', 0, 'gteq').execute()

    def by_code(self, attribute_code: str):
        return self.by_id(attribute_code)

    def get_types(self):
        endpoint = self.endpoint + '/types'
        response = self.client.get(self.client.url_for(endpoint))
        if response.ok:
            return [APIResponse(attr_type, self.client, endpoint) for attr_type in response.json()]


class CategorySearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='categories',
            client=client,
            model=Category
        )

    def get_root(self) -> Category:
        """The top level/default category. Every other category is a subcategory"""
        return self.execute()

    def get_all(self) -> list[Category]:
        """Retrieve a list of all categories"""
        self.query = self.query.replace('categories', 'categories/list') + 'searchCriteria[currentPage]=1'
        return self.execute()

    def by_name(self, name: str, exact: bool = True) -> Union[Category, List[Category]]:
        """Search categories by name

        :param name: the category name to search for
        :param exact: whether the name should be an exact match
        """
        self.query = self.query.replace('categories', 'categories/list')
        if exact:
            return self.add_criteria('name', name).execute()
        else:
            return self.add_criteria('name', f'%25{name}%25', 'like').execute()
