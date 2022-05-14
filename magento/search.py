from __future__ import annotations
from typing import Union

import magento
from .entities import Order, Entity, Category, OrderItem, Invoice
from .models import Product


class SearchQuery(object):

    def __init__(self, endpoint: str, client: magento.Client):
        if not isinstance(client, magento.Client):
            raise ValueError('Must provide a Client object to search with')

        self.client = client
        self.endpoint = endpoint
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
        response = self.client.request(self.query + self.fields)
        if response.ok:
            self._result = response.json()
        else:
            self._result = {'Bad Response': f'''
                Status Code: {response.status_code}
                Details:
                {response.json()}
'''}
        return self.result

    def by_id(self, entity_id: int | str) -> {}:
        self.query = self.query.strip('?') + str(entity_id)
        return self.execute()

    def by_number(self, increment_id: str) -> Entity:
        self.add_criteria('increment_id', increment_id).execute()
        if not self.result:
            return None
        if self.result_type is list:
            return self.result[0]
        return self.result

    def reset(self) -> None:
        self._result = {}
        self.fields = ''
        self.query = self.client.BASE_URL + self.endpoint + '/?'

    def validate_result(self) -> {} | list[{}]:
        # API Request error
        assert not self._result.get('Bad Response')
        # If fields restricted      ->    result is dict with one key, 'items'
        # If fields unrestricted    ->    result will have 'total_count' and 'items' keys
        if self.fields or self._result.get('total_count', None) is not None:
            return self._result.get('items', [{}])
        # Direct request by ID will have result of single entity, as dict
        return self._result

    def save_result(self, filepath):
        if not self.result:
            data = {}
        else:
            result = self.result if self.result_type is list else [self.result]
            data = [obj.json if isinstance(obj, Entity) else obj for obj in result]

        self.client.save_data(data, filepath)

    @property
    def result(self):
        return self.validate_result()

    @property
    def result_count(self) -> int:
        # Restricted fields -> result will be in the format {'items': None} or {'items': [{},{},...,{}]}
        if self.fields:
            items = self._result.get('items')
            if items is None:
                return 0
            return len(items)
        # Unrestricted fields, any result from a search endpoint will have 3 keys
        # Therefore, if not 3 keys it must be either
        #   1. Result from direct access by Id -> dict with 10+ keys
        #   2. Query not executed yet -> {} -> 0 keys
        if len(self._result) != 3:
            if not self._result:
                return 0
            return 1
        # Actual search queries will have result dict with 3 keys, one of which is 'total_count'
        return self._result.get('total_count', 0)

    @property
    def result_type(self):
        return type(self.result)


class OrderSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(endpoint='orders',
                         client=client)

    @property
    def result(self):
        result = self.validate_result()
        if not result:
            return None
        if type(result) is list:
            return [Order(order, self.client) for order in result]
        return Order(result, self.client)


class InvoiceSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(endpoint='invoices',
                         client=client)

    @property
    def result(self):
        result = self.validate_result()
        if not result:
            return None
        if type(result) is list:
            return Invoice(result[0])
        return Invoice(result)

    def by_order_id(self, order_id):
        return self.add_criteria(field='order_id',
                                 value=order_id).execute()

    def by_order(self, order):
        return self.by_order_id(order.id)

    def by_order_number(self, order_number):
        if order := self.client.orders.by_number(order_number):
            return self.by_order(order)


class ProductSearch(SearchQuery):

    def __init__(self, client):
        super().__init__(endpoint='products',
                         client=client)

    @property
    def result(self):
        result = self.validate_result()
        if not result:
            return None
        if type(result) is list:
            return [Product(p, self.client) for p in result]
        return Product(result, self.client)

    def by_sku(self, sku):
        # Convert to url-encodable sku; Query url is same structure as for id
        return self.by_id(sku.replace('/', '%2F'))

    def get_stock(self, sku):
        return self.by_sku(sku).stock


class CategorySearch(SearchQuery):

    def __init__(self, client):
        super().__init__(endpoint='categories',
                         client=client)

    @property
    def result(self):
        result = self.validate_result()
        if not result:
            return {}
        if type(result) is list:
            return [Category(category, self.client) for category in result]
        return Category(result, self.client)

    def all(self):
        response = self.client.request(self.client.BASE_URL + 'categories')
        if response.ok:
            return Category(response.json(), self.client)

    def products_from_id(self, category_id):
        return self.by_id(category_id).products

    def order_items_from_id(self, category_id):
        skus = self.products_from_id(category_id)
        return self.client.search('orders/items').add_criteria(field='sku',
                                                               value=','.join(skus),
                                                               condition='in').execute()

    def orders_from_id(self, category_id, start, end=None):
        order_items = self.order_items_from_id(category_id)
        order_ids = ','.join(set([str(item['order_id']) for item in order_items]))
        orders = self.client.orders.add_criteria(
            # Criteria to match all order_ids we found
            field='entity_id',
            value=order_ids,
            condition='in'
        ).add_criteria(
            # Criteria to match order date range
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

