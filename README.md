# my-magento
MyMagento is a Python package that acts as both a Python client and wrapper for the Magento 2 REST API. 

It utilizes a central `Client` class, endpoint specific `SearchQuery` classes, and various API response wrapper `Model`/`Entity` classes, which, as a whole, offers a comprehensive yet intuitive interface that greatly simplifies and facilitates interaction with the Magento API.
<br>

## Installation
To install this package with pip:
```bash
pip install my-magento
```

## Getting Started: Configuring the Client
MyMagento uses the `Client` class for all interaction with the Magento API, and every other class in the package can only be instantiated if a `Client` object is passed to their constructor. This means that, to do literally anything, you'll first need to create and authenticate a `Client`

***

### Configure the Magento Account

The Magento account you use must be assigned a **User Role** that has the appropriate API resources include in its **Resource Access** settings 

This can be verified in Magento Admin by going to 
```
System -> Permissions -> User Roles -> {Role} -> Role Resources -> Resource Access
```
and ensuring that `Sales`, `Catalog`, `Customers`, and all other desired resources are included

***

### Initialize and Authenticate a Client

Authentication is very straightforward
1. Initialize a `Client` using your Magento Admin login credentials
2. Request a token either by specifying `login=True` at the time of `Client` instantiation, or by calling `authenticate()` at any point afterwards

```python
from magento import Client

api = Client(
  domain='website.com',
  username='username',
  password='password',
  login = False
)
api.authenticate()
```

Alternatively, use `Client.new()` to login with input prompts

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

### View/Validate the Access Token
The access token currently in use by a `Client` object can be accessed via its
- `ACCESS_TOKEN` - instance attribute that stores the token
- `token` - property that calls `authenticate()` if no `ACCESS_TOKEN` has been set

You can call the `validate()` method to verify that the access token isn't expired

***

### Saving/Loading Client Configurations

A `Client` instance can be saved to/loaded from various formats
```python
import json
from magento import Client

# Save to/Load from JSON string, pickle string, or dict
json_str = api.to_json()
json_api = Client.from_json(json_str)

pickle_bytes = api.to_pickle() 
pickle_api = Client.load(pickle_bytes)

json_dict = json.loads(api.to_json())
dict_api = Client(**json_dict, login=False)
```

***

### Manually Set the Access Token

If you'd like to use this package but your site doesn't use the standard token authentication endpoint/workflow (ex. it uses 2FA), you can simply generate the token as you normally would, then set the `Client` access token manually. This can be done multiple ways: 

1. Directly set the `ACCESS_TOKEN` on an already initialized `Client`. Verify it by calling `validate()`

```python
token = "fsdkjgnewofgnQ$r@FDN8FJ38NDJKIINvblbahgfjgjgjgjfjfASJHNAHKSJDNKJASFDhoeodiqwahhahahahr02389jfd3nm981"
api.ACCESS_TOKEN = token
api.validate()
```

2. Initialize the `Client` and specify the `token` parameter. Ensure to use `login=False` so no attempt is made to generate a token

```python
api = magento.Client(
  domain="website.com",
  username="username",
  password="password",
  token=token,
  login=False   
)
```
3. Load the configuration from a previously saved pickle string, JSON string, or dictionary.

<br>

Regardless of how it's done, the key is to avoid calling `authenticate()`, as it would request a new token
