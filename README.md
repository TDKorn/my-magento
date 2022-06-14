# MyMagento (my-magento)
A Python package to help simplify interaction with the Magento 2 REST API.

***

## Why MyMagento?

After you [`authenticate()`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/clients.py#L55) 
a [`Client`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/clients.py#L11),
you'll never have to worry about formatting your Magento 2 REST API calls again - simply build your store's custom [`url_for()`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/clients.py#L93)
the API `endpoint` of your choice, then call [`request()`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/clients.py#L78)

If an [`endpoint`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/clients.py#L44)
supports the [`searchCriteria`](https://devdocs.magento.com/guides/v2.4/rest/performing-searches.html)
interface, you can use a [`SearchQuery`](https://github.com/TDKorn/my-magento/wiki/Search-Tutorial-Overview#SearchQuery) 
object to perform a [`search()`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/clients.py#L42) 
— just [`add_criteria()`](https://github.com/TDKorn/my-magento/wiki/Search-Tutorial-Overview#adding-criteria)
, [`restrict_fields()`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/search.py#L72)
, and [`execute()`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/search.py#L84) 
your [`query`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/search.py#L17). 
It will [`parse()`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/search.py#L143)
the response data, and, when possible, return the [`result`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/search.py#L101)
wrapped in one of the [`Model`](https://github.com/TDKorn/my-magento/blob/c2e7f6d11dd541e1ff3f2d5fd7f9f329d51f95b8/magento/models.py) 
or [`Entity`](https://github.com/TDKorn/my-magento/blob/c2e7f6d11dd541e1ff3f2d5fd7f9f329d51f95b8/magento/entities.py)
classes

***

## Installation
To install this package with pip:
```bash
pip install my-magento
```


## Documentation

Please see the [wiki](https://github.com/TDKorn/my-magento/wiki) for slightly more information

***

## Sample Usage
As mentioned above, you can use a [```Client```](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/clients.py#L11) to login and make requests to any Magento 2 REST API endpoint
```python
from magento import Client

api = Client('website.com','username', 'password')
endpoint = api.url_for("products/links/types", scope='')

response = api.request(endpoint)
print(url, response.json(), sep='\n')
```
Output:
```python
2022-06-14 00:55:42 INFO   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
2022-06-14 00:55:43 INFO   |[ MyMagento | website_username ]|:  Logged in to username

https://www.website.com/rest/V1/products/links/types
[{'code': 1, 'name': 'related'}, {'code': 5, 'name': 'crosssell'}, {'code': 4, 'name': 'upsell'}, {'code': 3, 'name': 'associated'}]
```

 <br>
 
 -  **TIP**: For detailed response data, search an endpoint [`by_id()`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/search.py#L90)


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



This package (and README) is fr a work in progress, so raw data will be returned if no wrapper class exists for a given endpoint yet. It will always [`validate_result`](https://github.com/TDKorn/my-magento/blob/e2ee60805387551f835b81a8dc80e320381a7695/magento/search.py#L110) first though so you should be okay. I am just disclaiming the disclaim here.
