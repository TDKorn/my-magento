from __future__ import annotations
from typing import Union, Iterable
from .entities import Order, Invoice
from .models import Product, Category
from . import clients


class SearchQuery:

    def __init__(self, endpoint: str, client: clients.Client, entity=None):
        if not isinstance(client, clients.Client):
            raise TypeError(f'client type must be {clients.Client}')

        self.client = client
        self.endpoint = endpoint
        self.Entity = entity
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

    @property
    def result(self):
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

    def parse(self, data):
        """Parses the API response and returns the corresponding entity/model object"""
        if self.Entity is not None:
            return self.Entity(data, self.client)   # SearchQuery subclasses return corresponding Entity/Model
        # General SearchQuery returns the raw data
        return data

    def reset(self) -> None:
        self._result = {}
        self.fields = ''
        self.query = self.client.url_for(self.endpoint) + '/?'

    @property
    def result_count(self):
        return len(self.result) if self._result else 0

    @property
    def result_type(self):
        return type(self.result)


class OrderSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='orders',
            client=client,
            entity=Order
        )


class InvoiceSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='invoices',
            client=client,
            entity=Invoice
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
            entity=Product
        )

    def by_id(self, item_id: Union[int, str]) -> {}:
        return self.add_criteria(
            field='entity_id',  # Product has no "entity_id" field in API responses, just "id"
            value=item_id       # But to search by the "id" field, need to use "entity_id"
        ).execute()

    def by_sku(self, sku) -> Product:
        return super().by_id(self.Entity.encode(sku))

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


class CategorySearch(SearchQuery):

    def __init__(self, client):
        super().__init__(
            endpoint='categories',
            client=client,
            entity=Category
        )

    def get_root(self) -> Category:
        """The top level/default category. Every other category is a subcategory"""
        return self.execute()

    def get_all(self) -> list[Category]:
        """Retrieve a list of all categories"""
        self.query = self.query.replace('categories', 'categories/list') + 'searchCriteria[currentPage]=1'
        return self.execute()

    def by_name(self, name: str) -> Category:
        """Search for a category by name"""
        return self.add_criteria('name', name).execute()
