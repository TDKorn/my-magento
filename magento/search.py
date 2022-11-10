from __future__ import annotations
from typing import Union
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
        self.query = self.client.BASE_URL + endpoint + '/?'
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
        self.query = self.client.BASE_URL + self.endpoint + '/?'

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
        self.query = self.client.url_for(
            endpoint='products/{}'.format(
                sku.replace('/', '%2F')
            )
        )
        return self.execute()

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

    def get_parent(self):
        """The top level/default category. Every other category is a subcategory"""
        return self.execute()

    def get_all(self):
        """Retrieve all categories"""
        parent = self.get_parent()
        if isinstance(parent, Category):
            return parent.subcategories

    def products_from_id(self, category_id):
        return self.by_id(category_id).products

    def order_items_from_id(self, category_id):
        skus = ','.join(self.products_from_id(category_id))
        query = self.client.search('orders/items')
        return query.add_criteria(
            field='sku',
            value=','.join(skus),
            condition = 'in'
        ).execute()

    def orders_from_id(self, category_id, start, end=None):
        order_items = self.order_items_from_id(category_id)
        order_ids = ','.join(set([str(item['order_id']) for item in order_items]))
        orders = self.client.orders

        orders.add_criteria(  # Criteria to match all order_ids we found
            field='entity_id',
            value=order_ids,
            condition='in'
        ).add_criteria(  # Criteria to match order date range
            field='created_at',
            value=start,
            condition='gt',
            group=1
        )
        if end:
            orders.add_criteria(
                field='created_at',
                value=end,
                condition='lteq',
                group=2
            )
        return orders.execute()
