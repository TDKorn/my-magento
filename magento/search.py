from __future__ import annotations
from typing import Union
import settings.config as config
from entities import Order


class SearchQuery(object):

    def __init__(self, endpoint: str):
        if config.client is None:
            raise ProcessLookupError('No client client found. Please login using magento.Client()')

        self.client = config.client
        self.endpoint = endpoint
        self.query = self.client.BASE_URL + endpoint + '/?'
        self.fields = ''
        self._result = {}

    def add_criteria(self, field: str, value: str, **kwargs: object) -> SearchQuery:
        options = {
            'condition': 'eq',
            'group': 0,
            'filter': 0,
        }
        options.update(kwargs)
        # Group 0 Filter 0 -> Filter 0
        # Group 0 Filter 0 + Group 0 Filter 1 -< Filter 0 OR Filter 1
        # Group 0 Filter 0 + Group 1 Filter 0 -< Filter 0 AND Filter 0
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
                raise AttributeError('Invalid argument.Must be comma separated string or list/tuple.')
            fields = ','.join(fields)
        # 'entity_id' field required to initialize any object that inherits Entity
        if 'entity_id' not in fields:
            fields = ','.join([fields, 'entity_id'])

        self.fields = f'&fields=items[{fields}]'
        return self

    def execute(self):
        # Any search query is passed through execute(). Request is sent with client.get() so it will always login/validate
        response = self.client.get(self.query + self.fields)
        if response.ok:
            self._result = response.json()
        else:
            self._result = {'Response': f'''
                Status Code: {response.status_code}
                Details:
                {response.json()}
'''}
        return self.result

    def by_id(self, entity_id: int | str) -> {}:
        self.query = self.query.strip('?') + str(entity_id)
        self.execute()
        return self.result

    def by_number(self, increment_id: str) -> dict:
        self.add_criteria('increment_id', increment_id).execute()
        if not self.result:
            return {}
        if self.result_type is list:
            return self.result[0]
        return self.result

    def reset(self) -> None:
        self._result = {}
        self.fields = ''
        self.query = self.client.BASE_URL + self.endpoint + '/?'

    def get_result(self) -> {} | list[{}]:
        # API Request error
        if self._result.get('Response'):
            return self._result['Response']
        # If fields restricted      ->    result is dict with one key, 'items'
        # If fields unrestricted    ->    result will have 'total_count' and 'items' keys
        if self.fields or self._result.get('total_count', None) is not None:
            return self._result.get('items', [{}])
        # Direct request by ID will have result of single entity, as dict
        return self._result

    @property
    def result(self):
        return self.get_result()

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

    def __init__(self):
        super().__init__('orders')

    @property
    def result(self):
        result = self.get_result()
        if not result or isinstance(result, str):
            return {}
        if type(result) is list:
            return [Order(order) for order in result]
        return Order(result)


class InvoiceSearch(SearchQuery):

    def __init__(self):
        super().__init__('invoices')

    def by_order_id(self, order_id):
        return self.add_criteria('order_id', order_id).execute()

    def by_order(self, order):
        return self.by_order_id(order.id)

    def by_order_number(self, order_number):
        order = OrderSearch().by_number(order_number)
        if order:
            return self.by_order_id(order[0]['entity_id'])
