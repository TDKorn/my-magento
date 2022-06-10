# search.py

The `search` module contains the base `SearchQuery` class, as well as all of its endpoint-specific subclasses.


## magento.search.SearchQuery


```python

class SearchQuery:
    
    """Base class for all API endpoint search queries"""
    
    def __init__(self, endpoint: 'str', client: 'clients.Client', entity=None):
        """Initialize a search query
        
        :param endpoint: the base API endpoint. For example, "orders"
        :param client:   the Client object that will be used to create and make the search query request
        :param entity:   the API wrapper class to parse the response with; uses raw data if not specified
        """
```

### Adding Criteria    
Use the `add_criteria()` method to add criteria to your query

```python
def add_criteria(self, field, value, condition='eq', **kwargs) -> SearchQuery:
        """Add criteria to the search query
        
        :param field:       the API response field to apply search criteria to
        :param value:       the value of the API response field to filter by 
        :param condition:   the condition used to evaluate criteria and determine if there is a match
        :param kwargs:      additional search option arguments (ie. group and filter)
        :return:            the calling SearchQuery object
        """
```

Since the method returns the SearchQuery object, it can be called repeatedly

**NOTE: Only top level response fields/attributes of the endpoint can be specified**

<br>

### Additional Search Criteria Options

When adding search criteria with ```add_criteria()```, the following keyword arguments can be included 

- ```condition```:  the condition used to evaluate the criteria and determine if there is a match
- ```group```: filter group number
- ```filter```:     filter number (within the specified filter group)

<br>

Each call to ```add_criteria()``` will incorporate these keyword arguments by updating an `options` dict with default values

```python
options = {
    'condition': condition,  #"eq"
    'group': 0,
    'filter': 0
}
options.update(kwargs)
```


#### Conditions
  - When making a search request, criteria is evaluated using ```{field}{condition}{value}```
  - The below table includes some of the available `condition` values that can be used. For a full list, please see [the official documentation](https://devdocs.magento.com/guides/v2.4/rest/performing-searches.html)

<br>

| Condition | Equivalent Python Operator | Notes                                                                                                  |
|-----------|:--------------------------:|--------------------------------------------------------------------------------------------------------|
| "eq"      |             ==             | Default value, equivalent to `{field} == {value}`                                                      |
| "gt"      |             \>             |                                                                                                        |
| "lt"      |             \<             |                                                                                                        |
| "gteq"    |            \>=             |                                                                                                        |
| "lteq"    |            \<=             |                                                                                                        |
| "neq"     |             !=             |                                                                                                        |
| "in"      |            `in`            | Value must be a comma separated list. Matches are determined using<br/>```field in value.split(",")``` |

<br>

#### Filters and Filter Groups

- Each filter specifies the `field`, `condition`, and `value` of the criteria
- Searches that are filtered on multiple criteria require you to specify the criteria's filter and filter group index
  - Filters within the same filter group are evaluated as `Filter 0` OR `Filter 1`
  - If multiple filter groups are specified, matches will be evaluated as ```Group 0``` AND ```Group 1```
- If not specified, the filter and filter group are implicitly the 0th index
  - This means you don't need to specify these options unless you have multiple filters or filter groups
  - This also means if you try to search on multiple criteria, and your results looks kinda ✨glonky✨, this is probably why

<br>

### Sample Usage: Filters/Filter Groups

Let's say we want to find products that are
1. Disabled **OR** Virtual &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **AND**
2. Created before 2018


What could that possibly be used for? I don't know. I literally couldn't think of a normal example.

Anyways, clearly we need two Groups for the AND part, and one of them needs to have two Filters


```python
from magento.clients import Client
from magento.models import Product

# Get the ProductSearch object
api = Client('domain.com','username','password')
search = api.products     

#Add the criteria for disabled or virtual products created before 2018
search.add_criteria(
    field='status',
    value=Product.STATUS_DISABLED   # Group 0 Filter 0
).add_criteria(
    field='type_id',
    value='virtual',
    filter=1                        # Group 0 Filter 1
).add_criteria(
    field='created_at',
    value='2018-01-01',
    condition='lt',
    group=1                         # Group 1 Filter 0
).execute() 

print(search.result_count)
print(search.result)
```

For more information please see the official Magento documentation: [Search using REST endpoints](https://devdocs.magento.com/guides/v2.4/rest/performing-searches.html)

<br>

### Additional Methods
Eventually, I will write the rest of this. And the other 4(?) classes in this module. How do people have time for all this


        
``` python    
    by_id(self, item_id: 'int   str') -> '{}'
    
    by_number(self, increment_id: 'str')
    
    execute(self)
        Sends the search request through the active client.
    
    parse(self, data)
        Parses the API response and returns the corresponding entity/model object
    
    reset(self) -> 'None'
    
    restrict_fields(self, fields: 'Union[str, list, tuple]') -> 'SearchQuery'
        # Query -> &fields=items['field1,field2']
    
    validate_result(self) -> '{}   list[{}]'
        Returns the actual result, regardless of search approach
        Failed: response will always contain a "message" key
        Success:
            Search Query:   response contains up to 3 keys from ["items", "total_count", "search_criteria"]
            Direct Query:   response is the full entity/model response dict; typically has 20+ keys
    
    ----------------------------------------------------------------------
    Readonly properties defined here:
    
    result
    
    result_count
    
    result_type
```