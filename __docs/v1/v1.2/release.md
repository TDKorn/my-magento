# 🌟🤩 v1.2  -  Add Logging and (Better) Exceptions 🌟😚

Logging and exceptions - can you think of anything more exciting? 😩
- How about writing these long messages to inform the literal void about the changes? 😍🤩😍


## Major Changes 

- Add logging support to the package through `MagentoLogger`,  a new custom logging class for this package
- Update the `AuthenticationError` class to be more than just `pass`
- Added a `tests` folder and added `logger_test.py` to it

## MagentoLogger

### Summary

1. It's a custom logging class for the package that can be used like any other logger
2. It has custom log message formatting and a bunch of extra helper methods (and static methods) built in

You can create a ```MagentoLogger``` from scratch, or you can call it from the package or a ```Client```

### Sample
```python
# Use Client Logger
from magento import Client

>>> api = Client('website.com','username', 'password', login=False)
>>> api.logger.info('Hello from Client')

2022-06-17 00:18:07 INFO   |[ MyMagento | website_username ]|:  Hello from Client
```
***
```python
# Use Package Logger
import magento
>>> magento.logger.info("Hello from my-magento")  # stdout_level is WARNING for package logger


>>> magento.logger.warning("Hello from my-magento")  

2022-06-17 00:16:06 WARNING  |[ MyMagento | my-magento ]|:  Hello from my-magento
```
***
```python
# Create from scratch
from magento.utils import MagentoLogger    

>>> logger = MagentoLogger('magento_logger')
>>> logger.info('Hello')

2022-06-16 23:54:38 INFO   |[ MyMagento | magento_logger ]|:  Hello

>>> print(logger.handler_map)  # One of the many helper methods; maps handlers of a logger by type and name

{  
    'stream': {'MyMagento__magento_logger__INFO': <StreamHandler <stdout> (INFO)>},  # Default level is INFO
    'file': {  # FileHandlers are set to DEBUG; all handler names are based off stdout_level
        'MyMagento__magento_logger__INFO': { 
            'handler': <FileHandler C:\path\to\my-magento\magento_logger.log (DEBUG)>,
            'file': 'C:\\path\\to\\my-magento\\magento_logger.log'
        },
        'MyMagento__my-magento__WARNING': {  # Handler for the package, added to every MagentoLogger; stdout_level is WARNING 
            'handler': <FileHandler C:\path\to\my-magento\my-magento.log (DEBUG)>,
            'file': 'C:\\path\\to\\my-magento\\my-magento.log'
        }
    }
}
```
***
### More Info
- Each ```Client``` object logs to its own log file as well as a central log file
  - A ```MagentoLogger``` instance is attached to each ```Client``` object at the time of its initialization
  - Each ```MagentoLogger``` is associated with a client using its unique ```domain```/```username``` combination 
-  Access a `Client` logger via ```Client.logger``` or ```Client.get_logger()```
    - Note that ```get_logger()``` will return a new ```MagentoLogger``` instance but it does NOT automatically update the ```Client``` with the new logger
      - Meant to be a shortcut to quickly make a new one based off the ```Client```, since the ```domain```/```username``` combination is used to configure the logger/log files
    - Use ```Client.logger.setup_logger()``` to modify in place


```python
from magento import Client

api = Client('domain.com', 'username', 'password')

# Default Stdout Level is INFO
api.logger.debug("AYOOO")


# Log level can be changed in place though
api.logger.setup_logger(stdout_level="DEBUG")

True

# Or create and assign a new MagentoLogger object
api.logger = api.get_logger(stdout_level="DEBUG")

# Verify it worked
api.logger.debug("🤩")

2022-06-17 09:30:46 DEBUG   |[ MyMagento | domain_username ]|:  HELLO
```

- Currently the package log file is ```my-magento.log```  but it depends on the value of ```MagentoLogger.PACKAGE_LOG_NAME```
    - Regardless of the name, you can call ```MagentoLogger.get_package_handler()``` to retrieve the FileHandler that writes to it
- The log level for console logging can be set with the ```stdout_level``` param, but all log files are written to with ```DEBUG```

***

### MagentoLogger Class Variables
You can use/edit the class variables below to change how names, messages, etc. look and function. Why class variables?

1) They can be accessed easily for formatting outside the class
2) They can be used for name checking outside the class
3) They can still reliably and effortlessly (!!!) do both of the above whenever I change formats

Using the class variables means only the variables themselves will need to be changed to make package-wide updates

```python
class MagentoLogger:
    """Logging class used within the package

    :cvar PREFIX:           hardcoded prefix to use in log messages
    :cvar PACKAGE_LOG_NAME: the default name for the package logger
    :cvar CLIENT_LOG_NAME:  the default format for the client logger name
    :cvar LOG_MESSAGE:      the default format for the message component of log messages.
                            (Use magento.logger.LOG_MESSAGE for easy access)
    :cvar FORMATTER:        the default logging format
    :type FORMATTER:        logging.Formatter
    :cvar HANDLER_NAME      the default format for the names of handlers created by this package
    """

    PREFIX = "MyMagento"
    PACKAGE_LOG_NAME = "my-magento"
    CLIENT_LOG_NAME = "{domain}_{username}"
    HANDLER_NAME = '{}__{}__{}'.format(PREFIX, '{name}', '{stdout_level}')
    
    LOG_MESSAGE = "|[ {pfx} | {name} ]|:  {message}".format(
            pfx=PREFIX, name="{name}", message="{message}"
     )
    
     FORMATTER = logging.Formatter(
            fmt="%(asctime)s %(levelname)-5s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
     )
```

***



## AuthenticationError
 - Update ```AuthenticationError``` class to accept a ```Client``` and ```response``` as parameters
   - ```Client``` is used solely for its logger
   - ```response``` is the response that led to the exception being raised. 
 - If a ```response``` is provided, ```parse()``` adds to the exception/log message from the response body
 -  Once a exception message is built, it is logged using the ```Client```'s ```MagentoLogger``` before being raised
 -  Written specifically for token auth errors, but should be flexible enough to handle most bad API responses

## Client
* Added ```get_logger()```  method and  ```logger```  instance attribute
* Added ```log_level``` parameter to ```__init__()``` to set console log level (default is "INFO")
* Updated ```validate()``` and ```authenticate()```  methods to make use of the logger.
* Update ```validate()``` to raise an ```AuthenticationError``` if it fails now
  - Every method did that after checking anyways so like? Why not
* Updated ```to_pickle() 🥒``` and ```to_json()``` to not raise ```AuthenticationError``` after calling ```validate()```
  * ```to_json()``` also includes ```log_level``` key now so full settings can be loaded
* Changed ```authenticate()``` to catch the ```AuthenticationError``` raised by ```validate()```, then raise another ```AuthenticationError``` from it
  - Indicates that the token request was successful, but the validation failed... could be helpful for debugging without checking logs?
* Add type/return hints to help with the next step in this repo: documentation 😍😍(😭)