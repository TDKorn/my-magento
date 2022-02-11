# my-magento
A package to simplify the Magento 2 REST API. 



Temporary Readme!!  Taken from the commit message 😭😭

## clients.py
### MagentoClient
>The main user interface class

- ```authenticate()``` logs in with user credentials to retrieve access token
- ```get()``` sends authorized requests to API endpoints
- ```search()``` builds and executes search queries for a specified endpoint



## search.py
### SearchQuery
>Default class for querying API endpoints

- ```add_criteria()``` and restrict_fields() build the query
- ```execute()``` sends the API request through the active client
- ```result``` provides the result
- ```by_id()``` and ```by_number()``` methods should work for most endpoints


### OrderSearch
>Subclass of SearchQuery with additional methods for orders
    
- ```result``` returns magento.entities.Order objects

### InvoiceSearch
>Subclass of SearchQuery with additional methods for invoices

Methods are used to help simplify obtaining an order's invoice

* ```by_order_id()```
* ```by_order()```  
* ```by_order_number()```


## entities.py
>A module containing classes for the various models used by Magento. 

All objects have an ```entity_id```

- ```Entity```
- ```Order```
- ```Invoice```
- ```Customer```

