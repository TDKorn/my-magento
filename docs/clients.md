### magento.clients.Client


```python

class Client

 __init__(self, domain, username, password, user_agent=None, token=None, login=True):    

    """The class that handles all interaction with the API"""

    :param domain: 'str',
    :param username: 'str', 
    :param password: 'str',
    :param user_agent: 'str' = None, 
    :param token: 'str' = None,
    :param login 'bool' = True
    
```

<p>
<b>NOTES:</b>

- `domain` is in the form `"domain.com"`
- Use `login=False` to avoid authenticating credentials
</p><br>



```python
   Relevant Methods
   
   authenticate(self) -> bool
       """Request access token from the authentication endpoint."""
 
   request(self, url: str) -> requests.Response
       """Sends a request with the access token. Used for all internal requests"""
 
   search(self, endpoint: str) -> magento.search.SearchQuery
       """Initializes and returns a SearchQuery object corresponding to the specified endpoint"""
 
   url_for(self, endpoint: str) -> magento.search.SearchQuery
       """Returns the base API request url for the specified endpoint"""
 
   validate(self)
       """Sends an authorized request to a standard API endpoint"""
 
   ----------------------------------------------------------------------
   Class Methods
    
   @classmethod
   new(cls) -> cls
      """Prompts for input to log in to the API. Returns a client after validating the token"""
 
   ----------------------------------------------------------------------
   Properties
   
   @property
   orders
   """Returns a magento.search.OrderSearch object"""
   
   @property
   products
   """Returns a magento.search.ProductSearch object"""
   
   @property
   categories
      """Returns a magento.search.CategorySearch object"""
   
   @property
   invoices
      """Returns a magento.search.InvoiceSearch object"""
      
   @property
   headers
      """Authorization headers for API requests. Validates/reauthenticates the token before returning"""
  
   @property
   token
       """Returns or generates access token"""
                          
```

