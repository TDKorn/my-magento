# MyMagento
A Python package to help simplify interaction with the Magento 2 REST API.


## Why Use MyMagento?

### Once you [`authenticate()`](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L55) your credentials on a [`Client`](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L11), you'll never need to format a request to the Magento 2 REST API again.

```python
# Login using MyMagento
from magento import Client

>>> api = Client('website.com','username', 'password', login=False)
>>> api.authenticate()

2022-06-14 00:55:42 INFO   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
2022-06-14 00:55:43 INFO   |[ MyMagento | website_username ]|:  Logged in to username
```

### Simply build your store's [```url_for()```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L93) any API endpoint, then send a REST authorized  [`request()`](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L78)

```python
# URL to get the comments from credit memo 593
endpoint = api.url_for("creditmemo/593/comments")
response = api.request(endpoint)
print(response.json())

>>> {'items': [{'comment': 'Order was a "mistake"', 'created_at': '2022-01-20 16:28:49', 'entity_id': 531, 'is_customer_notified': 1, 'is_visible_on_front': 0, 'parent_id': 593}], 'search_criteria': {'filter_groups': [{'filters': [{'field': 'parent_id', 'value': '593', 'condition_type': 'eq'}]}]}, 'total_count': 1}
```

> NOTE: After obtaining a [```token```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py) , the package will [```validate()```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L77) and regenerate it as needed
***

### Search for and retrieve data from any [```endpoint```] using a [```SearchQuery```](https://github.com/TDKorn/my-magento/blob/main/magento/search.py) or one of its subclasses
<!-- using a :class:`magento.search.SearchQuery` -->



```python
>>> api.search('orders')
>>> api.orders
>>> api.search('orders/items')

>>> search_orders = api.orders
>>> search_items = api.search('orders/items')
>>> search_orders.add_criteria(
'created_at',
'2022-01-01 00:00:00',
condition='gt'
).execute()
>>> search_items.add_criteria('created_at', '2022-01-01 00:00:00', condition='gt').execute()
>>> print(type(search_orders), type(search_items))


```

```
>>> api.invoices.by_id(1099)
<~..>
>>> order = api.orders.by_number(000001112) # (number is "increment_id" field)
>>> 


```
#### Every class in the ```search``` module, and any user-created ```SearchQuery``` object, can
- Request data for an individual entity using built-in methods like [```by_id()```] or through user-defined queries through [```add_criteria()```]
- Build complex queries with search criteria to filter store data
- Return the response data using a wrapper class when possible (see [```models```] and [```entities```] modules)


### Search [```by_id()```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py)

#### You can search [```by_id()```] for any endpoint that uses the ```/{endpoint}/"{id}"``` request format (almost all of them).

```python
>>> product = api.products.by_sku("SKU62")
>>> print(product)

Magento Product: SKU62

# Access all data through attributes
>>> print("Product ID:", product.id, "\nProduct Stock:", product.stock)

Product ID: 24
Product Stock: 50
```
 - Create a ```SearchQuery``` with the endpoint of your choice, or use an existing subclass
 - Either
    1. Call `by_id()`, `by_number()`, or a subclass-specific search method
    OR
    2. add_criteria()` and `restrict_fields()` to define your own search filters, then `execute()` your query


:meth:`magento.search.SearchQuery.by_id()`

### Perform a [```search()```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L42) on a [valid REST ```endpoint```](https://devdocs.magento.com/guides/v2.4/rest/performing-searches.html) using a [```SearchQuery```](https://github.com/TDKorn/my-magento/wiki/Search-Tutorial-Overview#SearchQuery) object
#### Simply [```add_criteria()```](https://github.com/TDKorn/my-magento/wiki/Search-Tutorial-Overview#adding-criteria),
[```restrict_fields()```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L72),
and [```execute()```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L84)
your [```query```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L17)
##### Then let the package [```parse()```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L143)
the response data and return the [```result```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L101),
using a [```Model```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/models.py)
or [```Entity```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/entities.py)
class when possible.




### Features
* #### Easily build the custom  [```url_for()```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L93)  any REST API endpoint of your Magento 2 store
* #### Make a REST authorized [`request()`](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L78) to any url
* #### Automatically [```validate()```] and [`authenticate()`](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L55) the  [```token```] as needed

* #### [```search.py```](https://github.com/TDKorn/my-magento/blob/main/magento/search.py) module provides simplified yet high level support for [search using REST endpoints](https://devdocs.magento.com/guides/v2.4/rest/performing-searches.html)
* #### [```Model```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/models.py) and [```Entity```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/entities.py) API response wrapper classes make [```result```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L101) data easier to work with and provide access to endpoint specific methods
* #### ```SearchQuery``` subclasses like ```ProductSearch``` or [```InvoiceSearch```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L174) provide additional specialized methods


## Installation
To install this package with pip:
```bash
pip install my-magento
```

## Documentation

Please see the [wiki](https://github.com/TDKorn/my-magento/wiki) for slightly more information

***

## Sample Usage



### Make Raw Requests

As mentioned above, the [```Client```](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L11) is used to build and make requests to any Magento 2 REST API endpoint

Build the request for an endpoint with ```url_for()```, then send it with ```request()```. Note that scoped URLs can be built if needed.
```python
# URL to get the comments from credit memo 593
endpoint = api.url_for("creditmemo/593/comments")
response = api.request(endpoint)
print(response.json())

>>> {'items': [{'comment': 'Order was a "mistake"', 'created_at': '2022-01-20 16:28:49', 'entity_id': 531, 'is_customer_notified': 1, 'is_visible_on_front': 0, 'parent_id': 593}], 'search_criteria': {'filter_groups': [{'filters': [{'field': 'parent_id', 'value': '593', 'condition_type': 'eq'}]}]}, 'total_count': 1}
```

Please see https://magento.redoc.ly/ for a full list of API endpoints for your store's version of Magento.

***

### Simple Searches Using a SearchQuery (or Subclass)

If you'd prefer not to work with raw data or URLs, that's what ```MyMagento``` is for!

The [```search```](https://github.com/tdkorn/my-magento/wiki/search-tutorial-overview)
module contains a variety of ways to access data about your store. Each ```SearchQuery``` subclass has a corresponding API response wrapper class defined in the ```models``` or ```entities``` modules,
which parses responses and provides extra methods to update the store.

The `Client` provides easy access to ```SearchQuery``` objects
```python
>>> api.search('orders')
<magento.search.OrderSearch object at 0x000002973FD2BE20>

>>> api.orders
<magento.search.OrderSearch object at 0x000002973FD282B0>
```
Predefined simple search methods exist to retrieve a single item ```by_id()``` (or ```by_sku()``` for products), but
some subclasses have additional ways to search, which may return information with varying degrees of detail.


```python
>>> product = api.products.by_sku("SKU62")
>>> print(product)

Magento Product: SKU62

# Access all data through attributes
>>> print("Product ID:", product.id, "\nProduct Stock:", product.stock)

Product ID: 24
Product Stock: 50

>>> order = api.orders.by_number("000009949")   # increment_id
>>> print(order)
>>> print(order.items)

"Order Number 000009949 placed on 2022-01-19 21:18:20"
[<magento.entities.OrderItem object at 0x000002973FD28B50>, <magento.entities.OrderItem object at 0x000002933FD28D59>]
```
The extra methods mean there are many ways to retrieve data for a given entity
```python
# Get the order's corresponding invoice
>>> api.search('invoices').by_order_number("000009949")
>>> api.invoices.by_order_id(order.id)
>>> api.invoices.by_order(order)
>>> order.get_invoice()

<magento.entities.Invoice object at 0x000002973FCD1E70>
```

### Advanced Search

If you've used the Magento 2 API before, you'll know that trying to search an endpoint using its ```searchCriteria``` interface
leads to request URLs that are actually insane. It's one of the most painful things about Magento's API (and the motivation for the package).

With MyMagento, full searches can be constructed and queried in a straightforward and understandable way.
Please see the wiki for full information on how to build a query.


Searches using criteria can be advanced, or simple - for example, searching by entity id is just
```python
def by_entity_id(api, endpoint, entity_id):
    return api.search(endpoint).add_criteria(
        field='entity_id',
        value=entity_id
    ).execute()
```
But one thing that's guaranteed is that the URL is NEVER simple
```python
>>> print(search.query)

https://www.website.com/rest/V1/orders/?searchCriteria[filter_groups][0][filters][0][field]=entity_id&searchCriteria[filter_groups][0][filters][0][value]=92&searchCriteria[filter_groups][0][filters][0][condition_type]=eq
```

From the [example](https://github.com/TDKorn/my-magento/wiki/Search-Tutorial-Overview#sample-usage-filtersfilter-groups) in the wiki, Let's say we want to find products that are
1. Disabled **OR** Virtual &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **AND**
2. Created before 2018

```python
from magento.models import Product
>>> search = api.products

# Criteria No.1
>>> search.add_criteria('status', Product.STATUS_DISABLED).add_criteria('type_id', 'virtual', filter=1)
# Criteria No .2
>>> search.add_criteria('created_at','2018-01-01', condition='lt', group=1)        
```
Simple, right? But then the URL... 
```python
>>> print(search.query)
```
```shell
https://www.website.com/rest/V1/products/?searchCriteria[filter_groups][0][filters][0][field]=status&searchCriteria[filter_groups][0][filters][0][value]=2&searchCriteria[filter_groups][0][filters][0][condition_type]=eq&searchCriteria[filter_groups][0][filters][1][field]=type_id&searchCriteria[filter_groups][0][filters][1][value]=virtual&searchCriteria[filter_groups][0][filters][1][condition_type]=eq&searchCriteria[filter_groups][1][filters][0][field]=created_at&searchCriteria[filter_groups][1][filters][0][value]=2018-01-01&searchCriteria[filter_groups][1][filters][0][condition_type]=lt
```

#### Model/Entity Methods
The wrapper classes provide extra methods to update/access data, like ```Order.get_invoice()``` above
```python
# Get all child products that are in stock and more than $20  |   Endpoint -> f'configurable-products/{encoded_sku}/children'
>>> children = [child for child in product.get_children() if child.stock > 0 if child.price > 20]

# Get all their URL keys - custom attributes are unpacked for you
>>> child_urls = [child.custom_attributes.get('url_key') for child in children]
>>> print(children, child_urls, sep='\n')

[<magento.models.Product object at 0x000002973FD49180>, <magento.models.Product object at 0x000002973FD4BEE0>, <magento.models.Product object at 0x000002973FD48160>, {...}, <magento.models.Product object at 0x000002973FD493C0>]
['url-key-1','url-key-2','product-blahblah', {...}, 'another-url-key']

----

>>> product.update_stock(0)

"Updated stock to 0"

>>> if product.stock < 1:
    ...     product.update_status(Product.STATUS_DISABLED)

"Success. Updated Status: Disabled"

>>> if product.updated_at < '2016-01-01': # It ain't happening
    ...     product.delete(scope='all')
```


> **TIP**: For the most detailed response data, search an endpoint [`by_id()`](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L90)


***

```PYTHON
file = get_read_me('my-magento')
COMMIT_HASH = file.text.find("SHA").(... # or whatever)
link = f"https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/clients.py#L{line-num}"  # like .py#L22

for link ln file.text -> replace {COMMIT_HASH} --> ammend comment --> force push --> automate?? or just press ctrl + r

```



***

## Getting Started


### Configure the Magento Account

The Magento account you use must be assigned a **User Role** that has the appropriate API resources include in its **Resource Access** settings

This can be verified in Magento Admin by going to
```
System -> Permissions -> User Roles -> {Role} -> Role Resources -> Resource Access
```
and ensuring that `Sales`, `Catalog`, `Customers`, and all other desired resources are included

***

### Initialize and Authenticate a Client

Authentication is very straightforward. For full details please see the [client setup tutorial](https://github.com/TDKorn/my-magento/wiki/Client-Tutorial-Overview) in the wiki

```python
from magento import Client

api = Client('website.com','username', 'password', login=False)
api.authenticate()
```

You can also use ```Client.new()``` to login with input prompts

```python
api = Client.new()
print('\nAccess Token: ', api.ACCESS_TOKEN)
```

Output:

```bash
Domain: >? website.com
Username: >? username
Password: >? password
User Agent: >?
2022-06-14 00:55:42 INFO   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
2022-06-14 00:55:43 INFO   |[ MyMagento | website_username ]|:  Logged in to username

Access Token:  eyJraWQiIxIiwiYWxnIjoiSFMyNTYifQ.eyJ1aWQiOjI3LCJ1dHlwaWQiOjIsImlhdCI6MTY1NTE4MjU0MywiZXhwIjoxNjU1MTg2MTQzfQ.AbtkboAG_5R6CTsHmZwu_DiINJ7BKQ0_5sqHGJqcJVk
```


***

####  ⚠ 🔥 🥵 DISCLAIMER 😩 🩸 ⚠ ❗



This package (and README) is fr a work in progress, so raw data will be returned if no wrapper class exists for a given endpoint yet. It will always [`validate_result`](https://github.com/TDKorn/my-magento/blob/{COMMIT_HASH}/magento/search.py#L110) first though so you should be okay. I am just disclaiming the disclaim here.
